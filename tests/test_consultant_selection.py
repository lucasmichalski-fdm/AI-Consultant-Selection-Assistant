import unittest

from consultant_selection import Applicant, JobDescription, rank_applicants


class RankApplicantsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.job = JobDescription(
            required_skills=["Python", "Salesforce", "Stakeholder Management"],
            preferred_skills=["Prompt Engineering", "Power BI"],
            required_certifications=["AWS CCP"],
            behavior_requirements={"communication": 80, "adaptability": 75},
        )

    def test_ranks_best_fit_first(self) -> None:
        applicants = [
            Applicant(
                name="Alex",
                skills=["Python", "Salesforce", "Stakeholder Management", "Prompt Engineering"],
                certifications=["AWS CCP"],
                behavior_scores={"communication": 85, "adaptability": 80},
            ),
            Applicant(
                name="Jordan",
                skills=["Python", "Stakeholder Management"],
                certifications=[],
                behavior_scores={"communication": 70, "adaptability": 70},
            ),
        ]

        ranked = rank_applicants(self.job, applicants)

        self.assertEqual(ranked[0].name, "Alex")
        self.assertGreater(ranked[0].score, ranked[1].score)
        self.assertEqual(ranked[0].recommendation, "Strong fit")

    def test_highlights_skill_and_certification_gaps(self) -> None:
        applicants = [
            Applicant(
                name="Jordan",
                skills=["Python", "Stakeholder Management"],
                certifications=[],
                behavior_scores={"communication": 70, "adaptability": 70},
            )
        ]

        result = rank_applicants(self.job, applicants)[0]

        self.assertIn("salesforce", result.skill_gaps)
        self.assertIn("aws ccp", result.skill_gaps)
        self.assertIn("Missing required skills: salesforce", result.explanation)

    def test_handles_case_and_whitespace_normalization(self) -> None:
        applicants = [
            Applicant(
                name="Taylor",
                skills=[" python ", "SALESFORCE", "stakeholder management"],
                certifications=["aws ccp"],
                behavior_scores={"communication": 80, "adaptability": 75},
            )
        ]

        result = rank_applicants(self.job, applicants)[0]

        self.assertEqual(result.missing_required_skills, [])
        self.assertEqual(result.recommendation, "Strong fit")


if __name__ == "__main__":
    unittest.main()
