import streamlit as st
import asyncio
import aioboto3
import time
import os
import qrcode


async def main():
    image = st.camera_input("Please take a picture")

    if image is not None:
        # st.image(image, caption="Captured Image.")

        session = aioboto3.Session()
        bucket = os.environ.get("R2_BUCKET_NAME")
        s3_endpoint = os.environ.get("R2_S3_ENDPOINT")
        access_key = os.environ.get("R2_ACCESS_KEY_ID")
        secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
        domain = "https://void.meetups.city"

        async with session.client(
            "s3",
            endpoint_url=s3_endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        ) as s3:
            # unix timestamp
            timestamp = int(time.time())
            Key = f"gdgchennai/camera/{timestamp}.jpg"
            await s3.put_object(Bucket=bucket, Key=Key, Body=image.getvalue())
            image_url = f"{domain}/{Key}"
            # st.image(image_url, caption="Uploaded Image here from cdn")
            # create qr code
            qr_code_image = qrcode.make(image_url)
            # convert to byte stream
            qr_code_image = qr_code_image._img.convert("RGB")
            st.image(qr_code_image, caption="QR Code Image")
            st.download_button(
                label="Download Image",
                data=image.getvalue(),
                file_name=f"{timestamp}.jpg",
                mime="image/jpeg",
            )
            save_to_local(image=image, qr_image=qr_code_image, timestamp=timestamp)


def save_to_local(image, qr_image, timestamp):
    # Define the directory path using the timestamp
    directory = f"image_dump/{timestamp}"
    
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the file paths for the image and QR code
    image_path = os.path.join(directory, "image.jpg")
    qr_image_path = os.path.join(directory, "qr_image.jpg")
    
    # Save the image
    with open(image_path, "wb") as img_file:
        img_file.write(image.getvalue())
    
    # Save the QR code image
    qr_image.save(qr_image_path)
    
    print(f"Images saved to {directory}")


if __name__ == "__main__":
    asyncio.run(main())
