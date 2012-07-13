import numpy as np

from lib.constants import DATASET_ID, LABEL, SCHEMA, SIMPLETYPE
from lib.tasks.import_dataset import import_dataset
from models.dataset import Dataset
from models.observation import Observation
from test_calculator import TestCalculator


class TestCalculations(TestCalculator):

    def setUp(self):
        TestCalculator.setUp(self)
        self.calculations = [
            'rating',
            'gps',
            'amount + gps_alt',
            'amount - gps_alt',
            'amount + 5',
            'amount - gps_alt + 2.5',
            'amount * gps_alt',
            'amount / gps_alt',
            'amount * gps_alt / 2.5',
            'amount + gps_alt * gps_precision',
            '(amount + gps_alt) * gps_precision',
            'amount = 2',
            '10 < amount',
            '10 < amount + gps_alt',
            'not amount = 2',
            'not(amount = 2)',
            'amount = 2 and 10 < amount',
            'amount = 2 or 10 < amount',
            'not not amount = 2 or 10 < amount',
            'not amount = 2 or 10 < amount',
            '(not amount = 2) or 10 < amount',
            'not(amount = 2 or 10 < amount)',
            'amount ^ 3',
            '(amount + gps_alt) ^ 2 + 100',
            '-amount',
            '-amount < gps_alt - 100',
            'rating in ["delectible"]',
            'risk_factor in ["low_risk"]',
            'amount in ["9.0", "2.0", "20.0"]',
            '(risk_factor in ["low_risk"]) and (amount in ["9.0", "20.0"])',
        ]
        self.places = 5

    def _test_calculation_results(self, name, formula):
            unslug_name = name
            name = self.column_labels_to_slugs[unslug_name]

            # test that updated dataframe persisted
            self.dframe = Observation.find(self.dataset, as_df=True)
            self.assertTrue(name in self.dframe.columns)

            # test new number of columns
            self.added_num_cols += 1
            self.assertEqual(self.start_num_cols + self.added_num_cols,
                             len(self.dframe.columns.tolist()))

            # test that the schema is up to date
            dataset = Dataset.find_one(self.dataset[DATASET_ID])
            self.assertTrue(SCHEMA in dataset.keys())
            self.assertTrue(isinstance(dataset[SCHEMA], dict))
            schema = dataset[SCHEMA]

            # test slugified column names
            self.slugified_key_list.append(name)
            self.assertEqual(sorted(schema.keys()),
                             sorted(self.slugified_key_list))

            # test column labels
            self.label_list.append(unslug_name)
            labels = [schema[col][LABEL] for col in schema.keys()]
            self.assertEqual(sorted(labels), sorted(self.label_list))

            # test result of calculation
            formula = self.column_labels_to_slugs[formula]

            for idx, row in self.dframe.iterrows():
                try:
                    result = np.float64(row[name])
                    stored = np.float64(row[formula])
                    # np.nan != np.nan, continue if we have two nan values
                    if np.isnan(result) and np.isnan(stored):
                        continue
                    msg = self._equal_msg(result, stored, formula)
                    self.assertAlmostEqual(result, stored, self.places, msg)
                except ValueError:
                    msg = self._equal_msg(row[name], row[formula], formula)
                    self.assertEqual(row[name], row[formula], msg)

    def test_calculator_with_delay(self):
        self._test_calculator()

    def test_calculator_without_delay(self):
        self._test_calculator(delay=False)
