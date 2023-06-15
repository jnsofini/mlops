from prefect import flow
from prefect_email import EmailServerCredentials, email_send_message
from typing import List
from time import sleep
# import click

# @click.command()
# @click.option(
#     "--email_addresses",
#     default=["example@mail.com"],
#     help="List of emails to send notification to"
# )


def create_email_block():
    credentials = EmailServerCredentials(
        username="mlphysics@gmail.com",
        password="---",  # must be an app password
    )
    credentials.save("email-block", overwrite=True)


@flow
def create_email_send_message_flow(email_addresses: List[str]):
    email_server_credentials = EmailServerCredentials.load("email-block")
    for email_address in email_addresses:
        subject = email_send_message.with_options(name=f"email {email_address}").submit(
            email_server_credentials=email_server_credentials,
            subject="Example Flow Notification When Task is completed",
            msg="This proves email_send_message works!",
            email_to=email_address,
        )

if __name__ == "__main__":
    create_email_block()
    sleep(5)
    create_email_send_message_flow(email_addresses=["--@yahoo.com"])