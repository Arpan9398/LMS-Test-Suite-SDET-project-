from pages.base_page import BasePage


class CoursesPage(BasePage):
    path = "/courses"

    def card(self, course_id: str):
        return self.by_id(f"course-card-{course_id}")

    def enroll_button(self, course_id: str):
        return self.by_id(f"enroll-{course_id}")

    def enrolled_badge(self, course_id: str):
        return self.by_id(f"enrolled-badge-{course_id}")

    def full_button(self, course_id: str):
        return self.by_id(f"full-badge-{course_id}")

    @property
    def message(self):
        return self.by_id("enroll-message")

    def enroll(self, course_id: str):
        self.enroll_button(course_id).click()
        return self


class MyCoursesPage(BasePage):
    path = "/my-courses"

    def course(self, course_id: str):
        return self.by_id(f"my-course-{course_id}")

    @property
    def empty_message(self):
        return self.by_id("no-courses")
