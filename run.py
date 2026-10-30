from main import analyze_message, analyze_url, analyze_qr, print_result


def main():
    while True:
        print("\n================================")
        print("       REAL-TIME SCAM SHIELD")
        print("================================")
        print("1. Check a message")
        print("2. Check a URL")
        print("3. Scan a QR code")
        print("4. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            text = input("\nPaste your message:\n")
            result = analyze_message(text)
            print_result(result)

        elif choice == "2":
            url = input("\nPaste your URL:\n")
            result = analyze_url(url)
            print_result(result)

        elif choice == "3":
            image_path = input("\nEnter QR image path:\n")
            result = analyze_qr(image_path)
            print_result(result)

        elif choice == "4":
            print("\nThank you for using Scam Shield!")
            break

        else:
            print("\nInvalid option. Please choose 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()