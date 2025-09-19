cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Development.Module
  REQUIRED)

python_add_library(
  std_base_toknzer MODULE 
  std_base_toknzer_module.c 
  _tokenize.c
  lexer/buffer.c
  lexer/lexer.c
  lexer/state.c
  tokenizer/helpers.c
  tokenizer/readline_tokenizer.c
  tokenizer/string_tokenizer.c
  tokenizer/utf8_tokenizer.c
  WITH_SOABI
)

install(TARGETS std_base_toknzer DESTINATION .)
