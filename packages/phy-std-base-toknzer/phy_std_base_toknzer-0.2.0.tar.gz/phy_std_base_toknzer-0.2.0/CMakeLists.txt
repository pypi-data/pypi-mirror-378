cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Development.Module
  REQUIRED)

python_add_library(
  _tokenize MODULE 
  std_base_toknzer/_tokenize/_tokenize_module.c 
  std_base_toknzer/_tokenize/_tokenize.c
  std_base_toknzer/_tokenize/lexer/buffer.c
  std_base_toknzer/_tokenize/lexer/lexer.c
  std_base_toknzer/_tokenize/lexer/state.c
  std_base_toknzer/_tokenize/tokenizer/helpers.c
  std_base_toknzer/_tokenize/tokenizer/readline_tokenizer.c
  std_base_toknzer/_tokenize/tokenizer/string_tokenizer.c
  std_base_toknzer/_tokenize/tokenizer/utf8_tokenizer.c
  WITH_SOABI
)

install(TARGETS _tokenize DESTINATION std_base_toknzer)
install(
  FILES std_base_toknzer/__init__.py
        std_base_toknzer/_tokenize.pyi
  DESTINATION std_base_toknzer
)
