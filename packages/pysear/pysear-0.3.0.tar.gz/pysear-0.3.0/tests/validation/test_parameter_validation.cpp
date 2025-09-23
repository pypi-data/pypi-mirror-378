#include "tests/validation/test_parameter_validation.hpp"

#include <sys/stat.h>

#include <cstring>

#include "sear/sear.h"
#include "tests/unit_test_utilities.hpp"
#include "tests/unity/unity.h"

void test_handle_syntax_error() {
  char *request_json = get_sample(TEST_SYNTAX_ERROR_REQUEST_JSON, "r");
  std::string result_json_expected =
      get_json_sample(TEST_SYNTAX_ERROR_RESULT_JSON);

  sear_result_t *result = sear(request_json, strlen(request_json), false);

  TEST_ASSERT_EQUAL_STRING(result_json_expected.c_str(), result->result_json);
  TEST_ASSERT_EQUAL_INT32(result_json_expected.length(),
                          result->result_json_length);
  TEST_ASSERT_EQUAL_CHAR(0, result->result_json[result->result_json_length]);
}

void test_handle_syntax_error_not_json() {
  char *request_json = get_sample(TEST_SYNTAX_ERROR_NOT_JSON_REQUEST_JSON, "r");
  std::string result_json_expected =
      get_json_sample(TEST_SYNTAX_ERROR_NOT_JSON_RESULT_JSON);

  sear_result_t *result = sear(request_json, strlen(request_json), false);

  TEST_ASSERT_EQUAL_STRING(result_json_expected.c_str(), result->result_json);
  TEST_ASSERT_EQUAL_INT32(result_json_expected.length(),
                          result->result_json_length);
  TEST_ASSERT_EQUAL_CHAR(0, result->result_json[result->result_json_length]);
}

void test_handle_syntax_error_binary_data() {
  char *request_json =
      get_sample(TEST_SYNTAX_ERROR_BINARY_DATA_REQUEST_JSON, "rb");
  std::string result_json_expected =
      get_json_sample(TEST_SYNTAX_ERROR_BINARY_DATA_RESULT_JSON);

  sear_result_t *result = sear(request_json, strlen(request_json), false);

  TEST_ASSERT_EQUAL_STRING(result_json_expected.c_str(), result->result_json);
  TEST_ASSERT_EQUAL_INT32(result_json_expected.length(),
                          result->result_json_length);
  TEST_ASSERT_EQUAL_CHAR(0, result->result_json[result->result_json_length]);
}

void test_parse_no_parameters_provided_error() {
  test_validation_errors(TEST_NO_PARAMETERS_PROVIDED_REQUEST_JSON,
                         TEST_PARAMETER_VALIDATION_ERROR_RESULT_JSON, false);
}

void test_parse_junk_json_error() {
  test_validation_errors(TEST_JUNK_JSON_REQUEST_JSON,
                         TEST_PARAMETER_VALIDATION_ERROR_RESULT_JSON, false);
}

void test_parse_parameters_junk_error() {
  test_validation_errors(TEST_PARAMETERS_JUNK_REQUEST_JSON,
                         TEST_PARAMETER_VALIDATION_ERROR_RESULT_JSON, false);
}

void test_parse_parameters_missing_error() {
  test_validation_errors(TEST_PARAMETERS_MISSING_REQUEST_JSON,
                         TEST_PARAMETER_VALIDATION_ERROR_RESULT_JSON, false);
}

void test_parse_extraneous_and_missing_parameters_error() {
  test_validation_errors(TEST_EXTRANEOUS_AND_MISSING_PARAMETERS_REQUEST_JSON,
                         TEST_PARAMETER_VALIDATION_ERROR_RESULT_JSON, false);
}

void test_parse_parameters_nonstring_error() {
  test_validation_errors(TEST_PARAMETERS_NONSTRING_REQUEST_JSON,
                         TEST_PARAMETER_VALIDATION_ERROR_RESULT_JSON, false);
}
