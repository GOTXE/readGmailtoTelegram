# readGmailtoTelegram
python script to read gmail messages and send body message to a telegram bot

Gmail to Telegram Notifications Script
Overview

This script provides functionality to receive notifications of incoming emails matching a specific subject in a Gmail inbox. When a new email with the specified subject is detected, it sends a message to a Telegram group using a Telegram bot, with the subject and the full body of the email. Additionally, it marks the new emails as read automatically after sending the notification.
Requirements

    Gmail API Credentials: You need API credentials from Gmail to authenticate with the service. This includes a credentials.json file.
    Telegram Bot Token: Obtain a token for your Telegram bot.
    Telegram Chat ID: You'll need the ID of the chat where you want to receive the notifications.
    Python 3: Ensure you have Python 3 installed on your system.

Setup Instructions

    Clone this repository to your local machine.
    Ensure you have the necessary requirements installed. You can install them using pip install -r requirements.txt.
    Place your credentials.json file in the same directory as the script.
    Complete the config.ini file with your Telegram bot token and chat ID.
    Run the script using Python 3.

Usage

Once the script is running, it will continuously monitor your Gmail inbox for new emails with the specified subject. When it finds a matching email, it will send a notification to your Telegram chat.
Author

    Author: Gotxe

Version History

    v1.4: Added exception and error handling, logging them to a file.
    v1.3: Expanded the text that can be sent, dividing it into multiple messages.
    v1.2: Expanded the text that can be sent in a single message.
    v1.1: Fixed issue where the script would truncate the body of the message.

## Terms of Use

This project is provided as-is, without any warranty. You are free to use, modify, and distribute the code as you see fit. However, the original author accepts no liability for any damages or issues arising from the use of this software.


Special thanks to the contributors of the libraries used in this project.
