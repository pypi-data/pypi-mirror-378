# Copyright © 2025, Alexander Suvorov
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import sys

from .core import generate_key, generate_nonce, encrypt_decrypt
from .database import CLMDatabase
from .auth import AuthManager


class ChronoLibrarianCLI:
    def __init__(self):
        self.MESSAGE_SEPARATOR = '|¶|'
        self.config_dir = Path.home() / ".config" / "clm"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.db = CLMDatabase(self.config_dir / "clm.db")
        self.auth = AuthManager(self.db)
        self.current_chat = None
        self.master_seed = None
        self.username = None
        self.chat_secrets = {}

    def safe_input(self, prompt):
        try:
            return input(prompt).strip()
        except UnicodeDecodeError:
            try:
                user_input = input(prompt)
                return user_input.encode('latin-1').decode('utf-8').strip()
            except:
                return input(prompt).encode('utf-8', errors='ignore').decode('utf-8').strip()

    def setup(self):
        print("🔄 Setting up Chrono-Library Messenger")
        print("=" * 50)

        username = self.safe_input("Enter your nickname: ")
        if not username:
            print("❌ Nickname is required")
            return False

        master_seed = self.safe_input("Enter your secret phrase: ")
        if not master_seed:
            print("❌ Secret phrase is required")
            return False

        confirm = self.safe_input("Repeat the secret phrase: ")
        if master_seed != confirm:
            print("❌ The phrases do not match")
            return False

        try:
            public_key = self.auth.generate_public_key(username, master_seed)
            self.db.set_config('username', username)
            self.db.set_config('public_key', public_key)

            print("✅ Setup complete!")
            print(f"👤 Your nickname: {username}")
            print("🔑 The public key has been saved.")
            return True
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False

    def login(self):
        print("🔐 Login to Chrono-Library Messenger")
        print("=" * 50)

        config = self.db.get_config()
        if 'public_key' not in config:
            print("❌ Initial setup required")
            return False

        self.username = config.get('username', '')
        stored_public_key = config.get('public_key', '')

        master_seed = self.safe_input("Enter your secret phrase: ")
        if not master_seed:
            print("❌ Secret phrase is required")
            return False

        if self.auth.verify_secret(self.username, master_seed, stored_public_key):
            self.master_seed = master_seed
            print("✅ Successful login!")
            return True
        else:
            print("❌ Invalid secret phrase")
            return False

    def safe_menu_execution(self, menu_func, *args):
        try:
            return menu_func(*args)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("⚠️  Returning to main menu...")
            input("\nPress Enter to continue...")
            return None

    def receive_message_outside_chat(self):
        print("\n📩 RECEIVE MESSAGE (NEW CHAT)")
        print("=" * 50)
        print("Enter the message pointer (JSON):")
        print("Or enter 'back' to return")

        payload_str = self.safe_input("")
        if payload_str.lower() == 'back':
            return

        try:
            payload_str_clean = payload_str.strip()
            if not payload_str_clean.endswith('}'):
                payload_str_clean = payload_str_clean + '}'
            if (payload_str_clean.startswith('"') and payload_str_clean.endswith('"')) or \
                    (payload_str_clean.startswith("'") and payload_str_clean.endswith("'")):
                payload_str_clean = payload_str_clean[1:-1]
            payload_str_clean = payload_str_clean.replace('\n', '').replace('\r', '').replace('\t', '')

            payload = json.loads(payload_str_clean)
            epoch_index = int(payload['e'])
            nonce = payload['n']
            ciphertext_hex = payload['d']
            ciphertext = bytes.fromhex(ciphertext_hex)

            chat_secret = self.safe_input("Enter chat secret to decrypt: ")
            if not chat_secret:
                print("❌ Secret required")
                return

            encryption_key = generate_key(chat_secret, epoch_index, nonce, len(ciphertext))

            try:
                message_bytes = encrypt_decrypt(ciphertext, encryption_key)
                signed_message = message_bytes.decode('utf-8')
            except UnicodeDecodeError:
                print("❌ Decryption failed - invalid secret")
                return

            if not signed_message.startswith('#') or self.MESSAGE_SEPARATOR not in signed_message:
                print("❌ Invalid message format - wrong secret?")
                return

            content = signed_message[1:]
            parts = content.split(self.MESSAGE_SEPARATOR)

            if len(parts) < 3:
                print("❌ Invalid message format")
                return

            chat_name_received, username_received, original_message = parts[0], parts[1], parts[2]

            if not self.is_valid_chat_name(chat_name_received):
                print("❌ Invalid chat name format in message")
                return

            existing_chats = self.db.get_chats()
            if chat_name_received in existing_chats:
                print(f"❌ Chat '{chat_name_received}' already exists")
                choice = self.safe_input("Go to this chat? (y/N): ").lower()
                if choice == 'y':
                    self.chat_details_menu(chat_name_received)
                return

            secret_hash = self.auth.hash_chat_secret(chat_name_received, chat_secret)
            self.db._ensure_chat_exists(chat_name_received, secret_hash)
            self.chat_secrets[chat_name_received] = chat_secret

            print(f"✅ New chat created: {chat_name_received}")
            print(f"👤 From: {username_received}")

            display_message = f"{username_received}: {original_message}"
            self.db.save_message('received', chat_name_received, epoch_index, nonce,
                                 display_message, payload_str_clean, chat_secret)

            print(f"📩 Message: {original_message}")
            input("\nPress Enter to continue...")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"❌ Invalid pointer format: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def is_valid_chat_name(self, chat_name: str) -> bool:
        if not chat_name or len(chat_name) > 50:
            return False
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return all(char not in chat_name for char in forbidden_chars)

    def _parse_payload(self, payload_str: str) -> Optional[dict]:
        try:
            payload_str_clean = payload_str.strip()
            if not payload_str_clean.endswith('}'):
                payload_str_clean = payload_str_clean + '}'
            if (payload_str_clean.startswith('"') and payload_str_clean.endswith('"')) or \
                    (payload_str_clean.startswith("'") and payload_str_clean.endswith("'")):
                payload_str_clean = payload_str_clean[1:-1]
            payload_str_clean = payload_str_clean.replace('\n', '').replace('\r', '').replace('\t', '')

            payload = json.loads(payload_str_clean)
            if 'e' not in payload or 'n' not in payload or 'd' not in payload:
                return None
            return payload
        except:
            return None

    def show_main_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("🌌 CHRONO-LIBRARY MESSENGER")
            print("=" * 50)
            print(f"👤 User: {self.username}")
            print("=" * 50)
            print("1. 💬 My chats")
            print("2. ➕ Create a new chat")
            print("3. ⚙️ Profile settings")
            print("4. 📩 Receive message (new chat)")
            print("5. 🚪 Exit")

            choice = self.safe_input("\nSelect an action (1-5): ")

            try:
                if choice == '1':
                    self.safe_menu_execution(self.show_chats_menu)
                elif choice == '2':
                    self.safe_menu_execution(self.create_chat)
                elif choice == '3':
                    self.safe_menu_execution(self.settings_menu)
                elif choice == '4':
                    self.receive_message_outside_chat()
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Wrong choice")
            except Exception as e:
                print(f"❌ Critical error in menu navigation: {e}")
                input("Press Enter to restart...")

    def get_chat_secret(self, chat_name: str) -> Optional[str]:
        if chat_name in self.chat_secrets:
            return self.chat_secrets[chat_name]

        stored_hash = self.db.get_chat_secret_hash(chat_name)
        if not stored_hash:
            return None

        secret = self.safe_input(f"Enter secret for chat '{chat_name}': ")
        if not secret:
            return None

        if self.auth.verify_chat_secret(chat_name, secret, stored_hash):
            self.chat_secrets[chat_name] = secret
            return secret
        else:
            print("❌ Invalid chat secret")
            return None

    def ensure_chat_secret(self, chat_name: str) -> Optional[str]:
        secret = self.get_chat_secret(chat_name)
        if secret is None:
            print("❌ Chat secret required")
        return secret

    def show_chats_menu(self):
        while True:
            chats = self.db.get_chats()
            if not chats:
                print("📭 There are no chats")
                return

            print("\n" + "=" * 50)
            print("💬 MY CHATS")
            print("=" * 50)

            for i, (chat_name, chat_info) in enumerate(sorted(chats.items()), 1):
                msg_count = self.db.get_message_count(chat_name, False)
                print(f"{i}. {chat_name} ({msg_count} messages)")

            print(f"{len(chats) + 1}. ↩️ Back")

            try:
                choice = int(self.safe_input(f"\nSelect a chat (1-{len(chats) + 1}): "))
                if 1 <= choice <= len(chats):
                    chat_name = list(sorted(chats.keys()))[choice - 1]
                    self.chat_details_menu(chat_name)
                elif choice == len(chats) + 1:
                    break
                else:
                    print("❌ Wrong choice")
            except ValueError:
                print("❌ Enter the number")

    def chat_details_menu(self, chat_name: str):
        chat_secret = self.ensure_chat_secret(chat_name)
        if not chat_secret:
            return

        while True:
            print(f"\n💬 CHAT: {chat_name}")
            print("1. 📨 Send message")
            print("2. 📩 Receive message")
            print("3. 📜 View history")
            print("4. 🔍 Search messages")
            print("5. 🗑️ Manage messages")
            print("6. 🧹 Clear history")
            print("7. 🔐 Change chat secret")
            print("8. ❌ Delete chat")
            print("9. ↩️ Back")

            choice = self.safe_input("\nSelect an action (1-9): ")

            if choice == '1':
                self.send_message_to_chat(chat_name, chat_secret)
            elif choice == '2':
                self.receive_message_menu(chat_name)
            elif choice == '3':
                self.show_chat_history(chat_name)
            elif choice == '4':
                self.search_messages_in_chat(chat_name)
            elif choice == '5':
                self.manage_messages_menu(chat_name)
            elif choice == '6':
                self.clear_chat_history(chat_name)
            elif choice == '7':
                self.change_chat_secret(chat_name)
            elif choice == '8':
                self.delete_chat(chat_name)
                break
            elif choice == '9':
                break
            else:
                print("❌ Wrong choice")

    def search_messages_in_chat(self, chat_name: str):
        print(f"\n🔍 SEARCH IN CHAT: {chat_name}")
        print("=" * 50)

        chat_secret = self.ensure_chat_secret(chat_name)
        if not chat_secret:
            return

        search_term = self.safe_input("Enter search term (or leave empty for all): ")
        messages = self.db.get_messages(chat_name, 0, True, chat_secret)

        if search_term:
            messages = [msg for msg in messages
                        if search_term.lower() in msg['message'].lower()]

        if not messages:
            print("📭 No messages found")
            return

        self.display_messages(messages, True)

        if len(messages) > 0:
            choice = self.safe_input("\nManage these messages? (y/N): ").lower()
            if choice == 'y':
                self.manage_messages_list(chat_name, messages)

    def manage_messages_menu(self, chat_name: str):
        while True:
            print(f"\n🗑️ MANAGE MESSAGES IN: {chat_name}")
            print("=" * 50)
            print("1. 📋 View all messages")
            print("2. 🔍 Search messages")
            print("3. 🗑️ View trash")
            print("4. ↩️ Back")

            choice = self.safe_input("\nSelect an action (1-4): ")

            if choice == '1':
                messages = self.db.get_messages(chat_name, 0, True)  # Включая удаленные
                self.manage_messages_list(chat_name, messages)
            elif choice == '2':
                self.search_messages_in_chat(chat_name)
            elif choice == '3':
                self.view_trash_in_chat(chat_name)
            elif choice == '4':
                break
            else:
                print("❌ Wrong choice")

    def view_trash_in_chat(self, chat_name: str):
        deleted_msgs = [msg for msg in self.db.get_messages(chat_name, 0, True)
                        if msg.get('is_deleted', 0) == 1]

        if not deleted_msgs:
            print("🗑️ Trash is empty in this chat")
            return

        print(f"\n🗑️ TRASH IN {chat_name} ({len(deleted_msgs)} messages)")
        print("=" * 50)

        for i, msg in enumerate(deleted_msgs, 1):
            time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M")
            preview = msg['message'][:30] + "..." if len(msg['message']) > 30 else msg['message']
            print(f"{i}. [{time_str}] {preview}")

        print(f"{len(deleted_msgs) + 1}. ↩️ Back")

        try:
            choice = int(self.safe_input(f"\nSelect a message (1-{len(deleted_msgs) + 1}): "))
            if 1 <= choice <= len(deleted_msgs):
                self.manage_deleted_message(deleted_msgs[choice - 1])
            elif choice != len(deleted_msgs) + 1:
                print("❌ Wrong choice")
        except ValueError:
            print("❌ Enter a valid number")

    def manage_messages_list(self, chat_name: str, messages: list):
        if not messages:
            print("📭 No messages to manage")
            return

        print(f"\n📋 MANAGING {len(messages)} MESSAGES IN: {chat_name}")
        print("=" * 50)

        for i, msg in enumerate(messages, 1):
            status = "🗑️ " if msg.get('is_deleted', 0) == 1 else "✅ "
            time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M")
            preview = msg['message'][:30] + "..." if len(msg['message']) > 30 else msg['message']
            print(f"{i}. {status}[{time_str}] {preview}")

        print(f"{len(messages) + 1}. ↩️ Back")

        try:
            choice = int(self.safe_input(f"\nSelect a message to manage (1-{len(messages) + 1}): "))
            if 1 <= choice <= len(messages):
                self.manage_single_message(messages[choice - 1])
            elif choice != len(messages) + 1:
                print("❌ Wrong choice")
        except ValueError:
            print("❌ Enter a valid number")

    def manage_single_message(self, msg):
        chat_name = msg['chat_name']
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        status = " (🗑️ deleted)" if msg.get('is_deleted', 0) == 1 else ""

        print(f"\n📝 MANAGING MESSAGE #{msg['id']}:")
        print(f"   Chat: {chat_name}")
        print(f"   Time: {time_str}{status}")
        print(f"   Type: {msg['type']}")
        print(f"   Content: {msg['message']}")

        if msg.get('is_deleted', 0) == 1:
            print("\n1. 🔄 Restore from trash")
            print("2. 🗑️ Delete permanently")
            print("3. ↩️ Back")
        else:
            print("\n1. 🗑️ Move to trash")
            print("2. ↩️ Back")

        choice = self.safe_input("\nSelect an action: ")

        if msg.get('is_deleted', 0) == 1:
            if choice == '1':
                self.db.restore_message(msg['id'])
                print("✅ Message has been restored.")
            elif choice == '2':
                confirm = self.safe_input("❌ Delete permanently? (y/N): ").lower()
                if confirm == 'y':
                    self.db.permanent_delete_message(msg['id'])
                    print("✅ Message has been permanently deleted.")
            elif choice != '3':
                print("❌ Wrong choice")
        else:
            if choice == '1':
                confirm = self.safe_input("❌ Move to trash? (y/N): ").lower()
                if confirm == 'y':
                    self.db.delete_message(msg['id'])
                    print("✅ Message moved to trash")
            elif choice != '2':
                print("❌ Wrong choice")

    def change_chat_secret(self, chat_name: str):
        print(f"\n🔐 Changing secret for chat: {chat_name}")

        current_secret = self.ensure_chat_secret(chat_name)
        if not current_secret:
            return

        new_secret = self.safe_input("Enter new secret phrase: ")
        if not new_secret:
            print("❌ Secret cannot be empty")
            return

        confirm = self.safe_input("Repeat new secret phrase: ")
        if new_secret != confirm:
            print("❌ Secrets do not match")
            return

        new_hash = self.auth.hash_chat_secret(chat_name, new_secret)
        self.db.set_chat_secret_hash(chat_name, new_hash)
        self.chat_secrets[chat_name] = new_secret

        print("✅ Chat secret updated!")

    def show_chat_history(self, chat_name: str):
        chat_secret = self.ensure_chat_secret(chat_name)
        if not chat_secret:
            return

        messages = self.db.get_messages(chat_name, 0, False, chat_secret)
        if not messages:
            print("📭 No messages")
            return

        self.display_messages(messages, True)

    def clear_chat_history(self, chat_name: str):
        message_count = self.db.get_message_count(chat_name, True)

        print(f"⚠️  Chat: {chat_name}")
        print(f"⚠️  Messages: {message_count} total")

        confirm = self.safe_input("❌ DELETE ALL messages in this chat? (y/N): ").lower()
        if confirm == 'y':
            self.db.clear_chat_history(chat_name)
            print(f"✅ All messages in the chat '{chat_name}' removed")
        else:
            print("❌ Deletion cancelled")

    def delete_chat(self, chat_name: str):
        message_count = self.db.get_message_count(chat_name, True)

        print(f"⚠️  Chat: {chat_name}")
        print(f"⚠️  Messages: {message_count} total")

        confirm = self.safe_input("❌ Delete this chat and ALL its messages? (y/N): ").lower()
        if confirm == 'y':
            self.db.delete_chat(chat_name)
            print(f"✅ Chat '{chat_name}' has been deleted")
        else:
            print("❌ Deletion cancelled")

    def send_message_menu(self):
        chats = self.db.get_chats()
        if not chats:
            print("❌ First, create a chat")
            return

        print("\n📨 SENDING A MESSAGE")
        print("=" * 50)

        for i, chat_name in enumerate(sorted(chats.keys()), 1):
            msg_count = self.db.get_message_count(chat_name, False)
            print(f"{i}. {chat_name} ({msg_count} messages)")

        print(f"{len(chats) + 1}. ↩️ Back")

        try:
            choice = int(self.safe_input(f"\nSelect a chat (1-{len(chats) + 1}): "))
            if 1 <= choice <= len(chats):
                chat_name = list(sorted(chats.keys()))[choice - 1]
                chat_secret = self.ensure_chat_secret(chat_name)
                if chat_secret:
                    self.send_message_to_chat(chat_name, chat_secret)
            elif choice != len(chats) + 1:
                print("❌ Wrong choice")
        except ValueError:
            print("❌ Enter the number")

    def send_message_to_chat(self, chat_name: str, chat_secret: str):
        print(f"\n📨 Sending to: {chat_name}")

        message = self.safe_input("Enter your message: ")
        if not message:
            print("❌ The message cannot be empty")
            return

        try:
            payload = self.send_message(message, chat_name, chat_secret)
            print("✅ Message sent and saved!")
            print("📋 Payload has been displayed above for sharing")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Sending error: {e}")

    def receive_message_menu(self, chat_name: str):
        print(f"\n📩 RECEIVE MESSAGE IN: {chat_name}")
        print("=" * 50)

        chat_secret = self.ensure_chat_secret(chat_name)
        if not chat_secret:
            return

        print("Enter the message pointer (JSON):")
        print("Or enter 'back' to return")

        payload_str = self.safe_input("")
        if payload_str.lower() == 'back':
            return

        try:
            message, error = self.receive_message(payload_str, chat_name)
            if error:
                print(f"❌ {error}")
            else:
                print(f"\n✅ Message received:")
                print(message)
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")

    def manage_deleted_message(self, msg):
        chat_name = msg['chat_name']
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n🗑️ Message #{msg['id']}:")
        print(f"   Chat: {chat_name}")
        print(f"   Time: {time_str}")
        print(f"   Type: {msg['type']}")
        print(f"   Content: {msg['message']}")

        print("\n1. 🔄 Restore")
        print("2. 🗑️ Delete permanently")
        print("3. ↩️ Back")

        choice = self.safe_input("\nSelect an action (1-3): ")

        if choice == '1':
            self.db.restore_message(msg['id'])
            print("✅ Message has been restored.")
            return True
        elif choice == '2':
            confirm = self.safe_input("❌ Delete permanently? (y/N): ").lower()
            if confirm == 'y':
                self.db.permanent_delete_message(msg['id'])
                print("✅ Message has been permanently deleted.")
                return True
        elif choice != '3':
            print("❌ Wrong choice")

        return False

    def settings_menu(self):
        while True:
            print("\n⚙️ PROFILE SETTINGS")
            print("=" * 50)
            print(f"👤 User: {self.username}")
            print("1. 🔑 Show public key")
            print("2. 🔄 Change secret phrase")
            print("3. 🗑️ Delete profile")
            print("4. ↩️ Back")

            choice = self.safe_input("\nSelect an action (1-4): ")

            if choice == '1':
                self.show_public_key()
            elif choice == '2':
                self.change_secret()
            elif choice == '3':
                self.delete_profile()
                break
            elif choice == '4':
                break
            else:
                print("❌ Wrong choice")

    def show_public_key(self):
        config = self.db.get_config()
        public_key = config.get('public_key', '')
        print(f"\n🔑 Your public key:")
        print(public_key)
        input("\nPress Enter to continue...")

    def change_secret(self):
        print("\n🔄 CHANGING THE SECRET PHRASE")
        print("=" * 50)

        current_secret = self.safe_input("Enter your current secret phrase: ")
        if not self.auth.verify_secret(self.username, current_secret,
                                       self.db.get_config().get('public_key', '')):
            print("❌ Invalid current phrase")
            return

        new_secret = self.safe_input("Enter a new secret phrase: ")
        if not new_secret:
            print("❌ The new phrase cannot be empty.")
            return

        confirm = self.safe_input("Repeat the new secret phrase: ")
        if new_secret != confirm:
            print("❌ The phrases do not match")
            return

        new_public_key = self.auth.generate_public_key(self.username, new_secret)
        self.db.set_config('public_key', new_public_key)
        self.master_seed = new_secret

        print("✅ Secret phrase changed!")

    def delete_profile(self):
        print("\n❌ DELETE PROFILE")
        print("=" * 50)
        print("⚠️  This action will delete:")
        print("   - All your chats")
        print("   - All messages")
        print("   - Profile settings")
        print("   - Unable to recover!")

        confirm = self.safe_input("\n❌ Enter 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("❌ Deletion cancelled")
            return

        db_path = self.config_dir / "clm.db"
        if db_path.exists():
            db_path.unlink()

        print("✅ Profile has been deleted. Please launch the program again.")
        sys.exit(0)

    def create_chat(self):
        print("\n➕ CREATING A NEW CHAT")
        print("=" * 50)

        name = self.safe_input("Enter the chat name: ")
        if not name:
            print("❌ Name is required")
            return

        existing_chats = self.db.get_chats()
        if name in existing_chats:
            print(f"❌ A chat with the name '{name}' already exists.")
            return

        secret = self.safe_input("Enter secret phrase for the chat: ")
        if not secret:
            print("❌ Secret phrase is required")
            return

        confirm = self.safe_input("Repeat secret phrase: ")
        if secret != confirm:
            print("❌ Secrets do not match")
            return

        try:
            secret_hash = self.auth.hash_chat_secret(name, secret)
            self.db._ensure_chat_exists(name, secret_hash)
            self.chat_secrets[name] = secret

            print(f"✅ Chat created: {name}")
        except Exception as e:
            print(f"❌ Error creating chat: {e}")

    def display_messages(self, messages, show_ids=False):
        for msg in messages:
            self.display_message(msg, show_ids)

        total = len(messages)
        print(f"\n📊 Showing {total} messages")
        input("\nPress Enter to continue...")

    def display_message(self, msg, show_ids=False):
        chat_name = msg['chat_name']
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        direction = "📤" if msg['type'] == 'sent' else "📥"
        msg_id = f" [#{msg['id']}]" if show_ids else ""

        display_text = msg['message']
        if msg['type'] == 'sent' and display_text.startswith('#') and self.MESSAGE_SEPARATOR in display_text:
            content = display_text[1:]
            parts = content.split(self.MESSAGE_SEPARATOR, 2)
            if len(parts) >= 3:
                display_text = f"{parts[1]}: {parts[2]}"

        print(f"\n{direction}{msg_id} [{time_str}] {chat_name}:")
        print(f"   {display_text}")

    def display_message_detail(self, msg):
        chat_name = msg['chat_name']
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        direction = "📤 Sent" if msg['type'] == 'sent' else "📥 Received"
        status = " (🗑️ deleted)" if msg.get('is_deleted', 0) == 1 else ""

        print(f"\n{direction}{status}")
        print(f"ID: #{msg['id']}")
        print(f"Chat: {chat_name}")
        print(f"Time: {time_str}")
        print(f"Content: {msg['message']}")

        if msg['type'] == 'sent' and not msg.get('is_deleted', 0):
            print(f"Pointer: {msg['payload']}")

        input("\nPress Enter to continue...")

    def send_message(self, message: str, chat_name: str, chat_secret: str) -> str:
        epoch_index = int(time.time())
        signed_message = f"#{chat_name}{self.MESSAGE_SEPARATOR}{self.username}{self.MESSAGE_SEPARATOR}{message}"

        nonce = generate_nonce(signed_message, epoch_index)
        message_bytes = signed_message.encode('utf-8')

        encryption_key = generate_key(chat_secret, epoch_index, nonce, len(message_bytes))
        ciphertext = encrypt_decrypt(message_bytes, encryption_key)

        payload = {
            'e': epoch_index,
            'n': nonce,
            'd': ciphertext.hex()
        }
        payload_str = json.dumps(payload, ensure_ascii=False)

        print("\n✅ Generated payload (copy this for recipient):")
        print("=" * 60)
        print(payload_str)
        print("=" * 60)
        print("📋 Copy the above text to share with the recipient")
        print("=" * 60)

        display_message = f"{self.username}: {message}"
        self.db.save_message('sent', chat_name, epoch_index, nonce, display_message, payload_str, chat_secret)
        return payload_str

    def receive_message(self, payload_str: str, chat_name: str) -> Tuple[Optional[str], Optional[str]]:
        existing_chats = self.db.get_chats()
        if chat_name not in existing_chats:
            return None, f"❌ Chat '{chat_name}' does not exist"

        chat_secret = self.ensure_chat_secret(chat_name)
        if not chat_secret:
            return None, "❌ Chat secret required"

        payload_str = payload_str.strip()

        if not payload_str.endswith('}'):
            payload_str = payload_str + '}'
        if (payload_str.startswith('"') and payload_str.endswith('"')) or \
                (payload_str.startswith("'") and payload_str.endswith("'")):
            payload_str = payload_str[1:-1]

        payload_str = payload_str.replace('\n', '').replace('\r', '').replace('\t', '')

        try:
            payload = json.loads(payload_str)
            epoch_index = int(payload['e'])
            nonce = payload['n']
            ciphertext_hex = payload['d']
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return None, "❌ Invalid pointer format"

        try:
            ciphertext = bytes.fromhex(ciphertext_hex)
        except ValueError:
            return None, "❌ Invalid ciphertext format"

        encryption_key = generate_key(chat_secret, epoch_index, nonce, len(ciphertext))

        try:
            message_bytes = encrypt_decrypt(ciphertext, encryption_key)
            signed_message = message_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return None, "❌ Decryption failed - invalid chat secret or corrupted message"

        if not signed_message.startswith('#') or self.MESSAGE_SEPARATOR not in signed_message:
            return None, "❌ Invalid message format - possible secret mismatch"

        content = signed_message[1:]
        parts = content.split(self.MESSAGE_SEPARATOR)

        if len(parts) < 3:
            return None, "❌ Invalid message format"

        chat_name_received, username_received, original_message = parts[0], parts[1], parts[2]

        if chat_name_received != chat_name:
            return None, f"❌ Message intended for different chat: {chat_name_received}"

        display_message = f"{username_received}: {original_message}"
        self.db.save_message('received', chat_name_received, epoch_index, nonce,
                             display_message, payload_str, chat_secret)
        return display_message, None


def main():
    cli = ChronoLibrarianCLI()

    config = cli.db.get_config()
    if 'public_key' not in config:
        print("🌌 Welcome to Chrono-Library Messenger!")
        print("=" * 50)
        if cli.setup():
            if cli.login():
                cli.show_main_menu()
    else:
        if cli.login():
            cli.show_main_menu()


if __name__ == "__main__":
    main()
