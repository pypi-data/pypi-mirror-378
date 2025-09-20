message(STATUS "running tester (glob mode: ${GLOB_MODE}): ${TESTER_COMMAND}")

if(WIN32)
    set(TERMINAL_CMD cmd /C)
else()
    set(TERMINAL_CMD bash -c)
endif()
set(TEST_FAILED FALSE)
set(_counter 0)
foreach(cmd ${TESTER_COMMAND})
    if(GLOB_MODE)
        # cmake-lint: disable=E1120
        separate_arguments(cmd)
        list(GET cmd 0 GLOB)
        list(GET cmd 1 NAME_A)
        list(GET cmd 2 NAME_B)
        list(GET cmd 3 ABS_TOL)
        list(GET cmd 4 REL_TOL)
        file(GLOB FILES RELATIVE ${SOURCE_PATH} ${GLOB})
        list(LENGTH FILES LENGTH)
        message(
            STATUS
                "Glob expression '${GLOB}' (${NAME_A}) found ${LENGTH} files."
        )
        if(${LENGTH} EQUAL 0)
            message(FATAL_ERROR "DIFF_DATA glob expression '${GLOB}' "
                                "did not match any files!"
            )
        endif()
        foreach(file ${FILES})
            math(EXPR _counter "${_counter}+1")
            set(LOG_FILE ${LOG_FILE_BASE}-${_counter}.txt)
            if("$ENV{HOSTNAME}" MATCHES "frontend.*")
                string(REPLACE "gpfs1" "../.." file ${file})
            endif()
            if("$ENV{HOSTNAME}" MATCHES "frontend.*")
                string(REPLACE "gpfs0" "../.." file ${file})
            endif()
            set(_source_file ${SOURCE_PATH}/${file})
            set(_binary_file ${BINARY_PATH}/${file})
            if(WIN32)
                file(TO_NATIVE_PATH "${_source_file}" _source_file)
                file(TO_NATIVE_PATH "${_binary_file}" _binary_file)
                # Prefix with extended path identifier \\?\
                set(_source_file "\\\\?\\${_source_file}")
                set(_binary_file "\\\\?\\${_binary_file}")
            endif()

            execute_process(
                COMMAND
                    ${SELECTED_DIFF_TOOL_PATH} ${_source_file} ${_binary_file}
                    -a ${NAME_A} -b ${NAME_B} --abs ${ABS_TOL} --rel ${REL_TOL}
                WORKING_DIRECTORY ${SOURCE_PATH}
                RESULT_VARIABLE EXIT_CODE
                OUTPUT_VARIABLE OUTPUT
                ERROR_VARIABLE OUTPUT ECHO_OUTPUT_VARIABLE ECHO_ERROR_VARIABLE
            )
            if(NOT EXIT_CODE STREQUAL "0")
                file(WRITE ${LOG_FILE} ${OUTPUT})
                message(
                    WARNING "Exit code: ${EXIT_CODE}; log file: ${LOG_FILE}"
                )
                set(TEST_FAILED TRUE)
            endif()
        endforeach()
    else()
        math(EXPR _counter "${_counter}+1")
        set(LOG_FILE ${LOG_FILE_BASE}-${_counter}.txt)
        execute_process(
            COMMAND ${TERMINAL_CMD} "${cmd}"
            WORKING_DIRECTORY ${SOURCE_PATH}
            RESULT_VARIABLE EXIT_CODE
            OUTPUT_VARIABLE OUTPUT
            ERROR_VARIABLE OUTPUT ECHO_OUTPUT_VARIABLE ECHO_ERROR_VARIABLE
        )
        if(NOT EXIT_CODE STREQUAL "0")
            file(WRITE ${LOG_FILE} ${OUTPUT})
            message(WARNING "Exit code: ${EXIT_CODE}; log file: ${LOG_FILE}")
            set(TEST_FAILED TRUE)
        endif()
    endif()
endforeach()
if(TEST_FAILED)
    message(FATAL_ERROR "One of the tests failed.")
endif()
