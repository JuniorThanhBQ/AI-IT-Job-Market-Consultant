from app.utils.text_parser import (
    clean_html_text,
    list_to_paragraph,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)


class TestTextParser:
    def test_clean_html_text_success(self):
        html_input = "<p>Hello&nbsp;<b>World</b>!</p>   Extra  spaces."

        result = clean_html_text(html_input)

        assert result == "Hello World! Extra spaces."

    def test_clean_html_text_empty(self):
        assert clean_html_text("") == ""
        assert clean_html_text(None) == ""

    def test_parse_to_list_from_list(self):
        input_data = ["<p>Item 1</p>", "Item 2"]

        result = parse_to_list(input_data)

        assert result == ["Item 1", "Item 2"]

    def test_parse_to_list_from_html_bullets(self):

        input_data = "<ul><li>Responsibility A</li><li>Responsibility B</li></ul>"

        result = parse_to_list(input_data)

        assert result == ["Responsibility A", "Responsibility B"]

    def test_parse_to_list_from_plain_text_bullets(self):

        input_data = "- Task 1\n* Task 2\n1. Task 3"

        result = parse_to_list(input_data)

        assert result == ["Task 1", "Task 2", "Task 3"]

    def test_list_to_paragraph(self):

        items = ["Sentence 1.", "Sentence 2."]

        result = list_to_paragraph(items)

        assert result == "Sentence 1.\nSentence 2."

    def test_resolve_company_name_from_scraped(self):
        assert resolve_company_name("Tech Corp", None, None, "source") == "Tech Corp"
        assert (
            resolve_company_name("Unknown", "Engineer at Google", None, "source")
            == "Google"
        )

    def test_resolve_company_name_from_url(self):
        result = resolve_company_name(
            None, "Software Engineer", "https://careers.microsoft.com/job", "source"
        )
        assert result == "Microsoft"

    def test_resolve_company_name_fallback(self):
        assert (
            resolve_company_name(None, None, None, "linkedin")
            == "Unspecified Employer (Linkedin)"
        )

    def test_resolve_job_description_scraped(self):
        result = resolve_job_description("Great job opportunity.", [], [])
        assert result == "Great job opportunity."

    def test_resolve_job_description_fallback_to_lists(self):
        resp = ["Coding", "Testing"]
        req = ["Python", "Pytest"]

        result = resolve_job_description("No description provided", resp, req)

        expected = "Responsibilities:\n- Coding\n- Testing\n\nRequirements:\n- Python\n- Pytest"
        assert result == expected
