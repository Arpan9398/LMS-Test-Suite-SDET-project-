from pages.base_page import BasePage


class AssignmentsPage(BasePage):
    path = "/assignments"

    def item(self, assignment_id: str):
        return self.by_id(f"assignment-{assignment_id}")

    def open_assignment(self, assignment_id: str):
        self.by_id(f"open-{assignment_id}").click()
        return AssignmentDetailPage(self.page, self.base_url)


class AssignmentDetailPage(BasePage):
    path = "/assignments"

    def open_by_id(self, assignment_id: str):
        self.page.goto(f"{self.base_url}/assignments/{assignment_id}")
        return self

    @property
    def message(self):
        return self.by_id("submission-message")

    @property
    def status(self):
        return self.by_id("submission-status")

    @property
    def title(self):
        return self.by_id("assignment-title")

    def submit_text(self, text: str):
        self.by_id("submission-text").fill(text)
        self.by_id("submit-assignment").click()
        return self

    def attach_file(self, path=None, name=None, mime="application/octet-stream", content: bytes = b""):
        """Attach a file from disk (path) or from memory (name + content)."""
        if path is not None:
            self.by_id("submission-file").set_input_files(str(path))
        else:
            self.by_id("submission-file").set_input_files(
                {"name": name, "mimeType": mime, "buffer": content})
        return self

    def submit(self):
        self.by_id("submit-assignment").click()
        return self
