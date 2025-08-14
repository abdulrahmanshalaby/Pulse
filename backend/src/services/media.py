
def finalize_upload(self, file_url: str, file_type: str):
        # Business rules example:
    if not file_url.startswith("https://"):
        raise ValueError("Invalid file URL")

    media = self.media_repository.create(file_url, file_type)
    return media