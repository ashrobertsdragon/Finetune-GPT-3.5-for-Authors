
# ProsePal Finetuner Tool

## Overview

ProsePal Finetuner is a versatile tool designed for fine-tuning language models on your custom datasets. This tool enables users to adapt language models to their specific needs, enhancing the model's performance on domain-specific texts.

## Features

- **Ebook Conversion**: Convert your ebooks to a compatible format for fine-tuning.
- **Custom Training**: Fine-tune language models using your text files.
- **Training Status Check**: Monitor the status of your fine-tuning process.
- **Download Fine-tuned Model**: Download your fine-tuned model for local use.

## Getting Started

### Landing Page

Navigate to the root URL to access the landing page of the ProsePal Finetuner tool.

### Instructions

Access detailed instructions on how to use the tool by navigating to `/finetune/instructions`.

### Privacy and Terms of Service

Read our privacy policy and terms of service at `/privacy` and `/terms`, respectively.

## Usage

### Contact Us

For support or inquiries, visit `/contact-us` to send us a message. We validate emails for format, deliverability, and SMTP to ensure communication reliability.

### Convert Ebook

Convert your ebook files to a text format suitable for fine-tuning by accessing `/convert-ebook`. We support various file types, including EPUB, PDF, DOCX, and plain text.

### Fine-tuning

Start the fine-tuning process by navigating to `/finetune`. Upload your text files and specify your requirements. Ensure your files are in UTF-8 format and within the size limits.

### Check Training Status

To check the status of your fine-tuning job, send a POST request to `/status` with your user folder's name.

### Download Fine-tuned Model

Once fine-tuning is complete, download your model from `/download/<path>`, where `<path>` is the path to your model file.

## Contributing

We welcome contributions to the ProsePal Finetuner tool. Please feel free to submit issues and pull requests.

## License

ProsePal Finetuner is open-sourced under the MIT license. See the LICENSE file for more details.
