import unittest
from datetime import datetime
from models import eTender, SupportingDoc

class TestETendersModels(unittest.TestCase):

    def test_from_api_response_valid(self):
        sample = {
            "id": "123",
            "description": "Upgrade of Roads",
            "datePublished": "2025-10-01T09:00:00",
            "closingDate": "2025-10-31T16:00:00",
            "tenderNo": "ET123",
            "categoryName": "Infrastructure",
            "tenderType": "Open",
            "departmentName": "Transport",
            "supportingDocuments": [
                {"name": "Specs.pdf", "url": "https://etenders.gov.za/docs/specs.pdf"}
            ]
        }

        tender = eTender.from_api_response(sample)
        self.assertIsNotNone(tender)
        self.assertEqual(tender.tender_number, "ET123")
        self.assertEqual(tender.department, "Transport")
        self.assertEqual(len(tender.supporting_docs), 1)

    def test_from_api_response_invalid_dates(self):
        sample = {
            "id": "123",
            "description": "Upgrade of Roads",
            "datePublished": "invalid-date",
            "closingDate": None,
            "tenderNo": "ET123",
            "categoryName": "Infrastructure",
            "tenderType": "Open",
            "departmentName": "Transport"
        }

        tender = eTender.from_api_response(sample)
        self.assertIsNone(tender.published_date)
        self.assertIsNone(tender.closing_date)

    def test_to_dict_structure(self):
        tender = eTender(
            title="Road Upgrade",
            description="Fix potholes",
            source="eTenders",
            published_date=datetime(2025, 10, 1, 9, 0),
            closing_date=datetime(2025, 10, 31, 16, 0),
            supporting_docs=[SupportingDoc("Doc", "https://example.com")],
            tags=[],
            tender_number="ET123",
            category="Infrastructure",
            tender_type="Open",
            department="Transport"
        )
        data = tender.to_dict()
        self.assertEqual(data["title"], "Road Upgrade")
        self.assertEqual(data["supporting_docs"][0]["url"], "https://example.com")
        self.assertEqual(data["department"], "Transport")

if __name__ == '__main__':
    unittest.main()
