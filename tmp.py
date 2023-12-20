

# locked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format

# import re
# import time

# # Test patterns
# patterns = [
#     r"^\d+$",                  # Matches one or more digits
#     r"^[A-Za-z]+$",            # Matches one or more alphabetic characters
#     r"^[A-Za-z0-9]+$",         # Matches one or more alphanumeric characters
#     r"^\w+@\w+\.\w+$"          # Matches a basic email address pattern
# ]

# # Test strings
# strings = [
#     "1234567890",
#     "abcdefg",
#     "abc123",
#     "john.doe@example.com"
# ]

# # Regex libraries to test
# libraries = {
#     "PCRE": re,
#     "RE2": re,
#     "Boost.Regex": re,
#     "Oniguruma": re,
# }

# # Perform tests
# for pattern in patterns:
#     print(f"Pattern: {pattern}")
#     for library, regex_module in libraries.items():
#         total_time = 0
#         for string in strings:
#             start_time = time.time()
#             regex_module.match(pattern, string)
#             end_time = time.time()
#             elapsed_time = end_time - start_time
#             total_time += elapsed_time

#         avg_time = total_time / len(strings)
#         print(f"{library}: Average Time: {avg_time:.6f} seconds")
#     print()
