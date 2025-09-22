#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "turboxl::turboxl_core" for configuration "Release"
set_property(TARGET turboxl::turboxl_core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(turboxl::turboxl_core PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libturboxl_core.a"
  )

list(APPEND _cmake_import_check_targets turboxl::turboxl_core )
list(APPEND _cmake_import_check_files_for_turboxl::turboxl_core "${_IMPORT_PREFIX}/lib/libturboxl_core.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
