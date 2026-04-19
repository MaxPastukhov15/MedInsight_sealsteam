import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pytest
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from analyse.analyse_disease import analyse_disease, load_data, normalize_id


class TestAnalyseDisease:
    """Test suite for analyse_disease function"""

    @pytest.fixture
    def sample_diagnoses(self):
        """Sample diagnoses dataframe"""
        return pd.DataFrame(
            {
                "diagnosis_code": ["J10", "J10.1", "J11", "A09"],
                "diagnosis_name": ["Influenza", "Influenza with pneumonia", "Influenza", "Gastroenteritis"],
            }
        )

    @pytest.fixture
    def sample_prescriptions(self):
        """Sample prescriptions dataframe"""
        return pd.DataFrame(
            {
                "patient_id": ["1", "2", "3", "1", "4", "5"],
                "diagnosis_code": ["J10", "J10.1", "J11", "J10", "J10", "A09"],
                "year": [2023, 2023, 2023, 2022, 2023, 2023],
            }
        )

    @pytest.fixture
    def sample_patients(self):
        """Sample patients dataframe"""
        return pd.DataFrame(
            {
                "patient_id": ["1", "2", "3", "4", "5"],
                "birth_dt": ["01/01/1980", "15/06/1995", "20/03/1970", "10/10/2000", "05/05/1985"],
                "gender": ["М", "Ж", "М", "Ж", "М"],
                "district": ["District A", "District B", "District A", "District A", "District C"],
            }
        )

    def test_analyse_disease_with_disease_code(self, sample_diagnoses, sample_prescriptions, sample_patients):
        """Test 1: analyse_disease correctly calculates metrics for a given disease_code and year"""
        result_json, file_id = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=sample_prescriptions,
            patients=sample_patients,
            disease_code="J10",
        )

        result = json.loads(result_json)

        # Verify structure
        assert "meta" in result
        assert "total_cases" in result
        assert "incidence_per_100k" in result
        assert "growth_rate_percent" in result
        assert "demographics" in result
        assert "top_districts" in result

        # Verify meta information
        assert result["meta"]["analysis_year"] == 2023
        assert result["meta"]["disease_target"] == "Influenza"
        assert result["meta"]["target_type"] == "code"
        assert result["meta"]["district_filter"] == "All"

        # Verify calculations (J10 appears 2 times in 2023: patient 1 and patient 4)
        assert result["total_cases"] == 2
        assert result["incidence_per_100k"] > 0

        # Verify file identifier
        assert file_id == "J10"

    def test_analyse_disease_with_disease_name(self, sample_diagnoses, sample_prescriptions, sample_patients):
        """Test 2: analyse_disease correctly calculates metrics for a given disease_name (matching multiple codes) and year"""
        result_json, file_id = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=sample_prescriptions,
            patients=sample_patients,
            disease_name="Influenza",
        )

        result = json.loads(result_json)

        # Verify meta information
        assert result["meta"]["disease_target"] == "Influenza"
        assert result["meta"]["target_type"] == "name_search"

        # Should match J10, J10.1, and J11 (all containing 'Influenza')
        # Total cases: patient 1 (J10), patient 2 (J10.1), patient 3 (J11), patient 4 (J10) = 4
        assert result["total_cases"] == 4

        # Verify demographics structure
        assert "sex_distribution" in result["demographics"]
        assert "age_stats" in result["demographics"]
        assert "age_groups" in result["demographics"]

        # Verify file identifier is sanitized disease name
        assert file_id == "Influenza"

    def test_analyse_disease_with_district_filter(self, sample_diagnoses, sample_prescriptions, sample_patients):
        """Test 3: analyse_disease correctly filters results by district"""
        result_json, file_id = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=sample_prescriptions,
            patients=sample_patients,
            disease_code="J10",
            district="District A",
        )

        result = json.loads(result_json)

        # Verify district filter in meta
        assert result["meta"]["district_filter"] == "District A"

        # J10 in 2023: patient 1 (District A) and patient 4 (District A) = 2 cases
        assert result["total_cases"] == 2

        # Verify population count is filtered
        # District A has patients: 1, 3, 4 (3 patients total)
        assert result["incidence_per_100k"] > 0

    def test_analyse_disease_no_disease_provided(self, sample_diagnoses, sample_prescriptions, sample_patients):
        """Test 4: that error is returned when neither disease_code nor disease_name is provided"""
        result_json, status = analyse_disease(
            year=2023, diagnoses=sample_diagnoses, prescriptions=sample_prescriptions, patients=sample_patients
        )

        result = json.loads(result_json)
        assert "error" in result
        assert status == "error"

    def test_analyse_disease_invalid_disease_name(self, sample_diagnoses, sample_prescriptions, sample_patients):
        """Test 5: that error is returned for non-existent disease name"""
        result_json, status = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=sample_prescriptions,
            patients=sample_patients,
            disease_name="NonExistentDisease",
        )

        result = json.loads(result_json)
        assert "error" in result
        assert "No diagnosis found" in result["error"]
        assert status == "error"

    def test_analyse_disease_unknown_code_logic(self, sample_diagnoses, sample_prescriptions, sample_patients):
        """Test 6: display_name fallback when code exists in input but not in diagnoses lookup"""
        result_json, file_id = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=sample_prescriptions,
            patients=sample_patients,
            disease_code="Z99",
        )

        result = json.loads(result_json)

        assert result["meta"]["disease_target"] == "Code Z99"
        assert file_id == "Z99"

    def test_analyse_disease_zero_population(self, sample_diagnoses, sample_prescriptions):
        """Test 7: Covers incidence_rate_100k = 0.0 (Line 129) when population is zero."""
        empty_patients = pd.DataFrame(columns=["patient_id", "birth_dt", "gender", "district"])

        result_json, _ = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=sample_prescriptions,
            patients=empty_patients,
            disease_code="J10",
        )

        result = json.loads(result_json)

        assert result["total_cases"] > 0
        assert result["incidence_per_100k"] == 0.0

    def test_analyse_disease_elderly_demographics(self, sample_diagnoses):
        """Test 8: Covers '60+' age group logic"""
        elderly_patients = pd.DataFrame(
            {"patient_id": ["1"], "birth_dt": ["01/01/1950"], "gender": ["M"], "district": ["District A"]}
        )

        elderly_prescriptions = pd.DataFrame({"patient_id": ["1"], "diagnosis_code": ["J10"], "year": [2023]})

        result_json, _ = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=elderly_prescriptions,
            patients=elderly_patients,
            disease_code="J10",
        )

        result = json.loads(result_json)

        assert result["demographics"]["age_groups"]["60+"] == 100.0

    def test_no_cases_found_logic(self, sample_diagnoses, sample_patients):
        """Test 9a: Empty df_current causing empty age_bins Series"""
        empty_prescriptions = pd.DataFrame(columns=["patient_id", "diagnosis_code", "year"])

        result_json, _ = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=empty_prescriptions,
            patients=sample_patients,
            disease_code="J10",
        )

        result = json.loads(result_json)

        assert result["demographics"]["age_groups"]["0-17"] == 0.0

        assert result["growth_rate_percent"] == 0.0
        assert result["total_cases"] == 0

    def test_growth_from_zero(self, sample_diagnoses, sample_patients):
        """Test 9b: count_prev == 0 BUT total_cases > 0 -> growth_rate 100.0"""
        custom_prescriptions = pd.DataFrame({"patient_id": ["1"], "diagnosis_code": ["J10"], "year": [2023]})

        result_json, _ = analyse_disease(
            year=2023,
            diagnoses=sample_diagnoses,
            prescriptions=custom_prescriptions,
            patients=sample_patients,
            disease_code="J10",
        )

        result = json.loads(result_json)

        assert result["total_cases"] == 1
        assert result["growth_rate_percent"] == 100.0


class TestLoadData:
    """Test suite for load_data function"""

    def test_load_data_missing_file(self):
        """Test 10: load_data raises FileNotFoundError when a data file is missing"""
        # Mock the paths to point to a non-existent directory
        with patch("analyse.analyse_disease.os.path.dirname") as mock_dirname:
            mock_dirname.return_value = "/non/existent/path"

            with pytest.raises(FileNotFoundError) as exc_info:
                load_data()

            assert "Could not find data files" in str(exc_info.value)

    @patch("analyse.analyse_disease.pd.read_parquet")
    def test_load_data_success(self, mock_read_parquet):
        """Test that load_data successfully returns all dataframes"""
        # Mock successful reads
        mock_df = pd.DataFrame({"test": [1, 2, 3]})
        mock_read_parquet.return_value = mock_df

        diagnoses, prescriptions, patients, medications = load_data()

        # Verify all four dataframes are returned
        assert diagnoses is not None
        assert prescriptions is not None
        assert patients is not None
        assert medications is not None

        # Verify read_parquet was called 4 times
        assert mock_read_parquet.call_count == 4


class TestNormalizeId:
    """Test suite for normalize_id function"""

    def test_normalize_id_integers(self):
        """Test 11a: normalize_id correctly cleans integer patient IDs"""
        series = pd.Series([1, 2, 3, 100])
        result = normalize_id(series)

        assert result.tolist() == ["1", "2", "3", "100"]
        assert result.dtype == object

    def test_normalize_id_floats(self):
        """Test 11b: normalize_id correctly removes .0 from float patient IDs"""
        series = pd.Series([123.0, 456.0, 789.0])
        result = normalize_id(series)

        assert result.tolist() == ["123", "456", "789"]

    def test_normalize_id_strings_with_whitespace(self):
        """Test 11c: normalize_id correctly strips whitespace from string patient IDs"""
        series = pd.Series(["  123  ", " 456", "789 "])
        result = normalize_id(series)

        assert result.tolist() == ["123", "456", "789"]

    def test_normalize_id_mixed_formats(self):
        """Test 11d: normalize_id handles mixed formats (integers, floats, strings)"""
        series = pd.Series([1, 2.0, "  3  ", 100.0, " 200"])
        result = normalize_id(series)

        assert result.tolist() == ["1", "2", "3", "100", "200"]

    def test_normalize_id_strings_without_decimal(self):
        """Test 11e: normalize_id preserves string IDs that don't end with .0"""
        series = pd.Series(["ABC123", "XYZ456", "123ABC"])
        result = normalize_id(series)

        assert result.tolist() == ["ABC123", "XYZ456", "123ABC"]

    def test_normalize_id_empty_series(self):
        """Test 11f: normalize_id handles empty series"""
        series = pd.Series([], dtype=object)
        result = normalize_id(series)

        assert len(result) == 0
        assert result.dtype == object
