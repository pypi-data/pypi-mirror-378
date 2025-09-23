BEGIN

CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_QUESTION_RUNS()
	returns string
	language javascript
	execute as owner as
	$$
        // Installs the handler for new question runs

        function logStatementWithRequestID(message, request_id) {
            snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                binds:[message, request_id, Object.keys(this)[0]]
            }).execute();
        }

        function escapeForSqlLiteral(inputString) {
            // First escape backslashes, then escape single quotes
            var escapedBackslashes = inputString.replace(/\\/g, "\\\\");
            var escapedSingleQuotes = escapedBackslashes.replace(/'/g, "''");
            return escapedSingleQuotes;
        }

        // Fetches the new question run request's from the CLEAN_ROOM_REQUESTS table and processes them

        try {
            var crRequestSql = "SELECT id AS request_id, " +
            " request_data:clean_room_id AS clean_room_id, " +
            " request_data:result_table AS result_table, " +
            " request_data:result_table_ddl AS result_table_ddl, " +
            " request_data:accounts AS accounts, " +
            " request_data:accountNames AS accountNames, " +
            " request_data:organizationNames AS organizationNames, " +
            " request_data:compute_account_id AS compute_account_id, " +
            " request_data:statement_hash AS statement_hash, " +
            " request_data:question_run_query AS question_run_query, " +
            " request_data:procedure_sql AS procedure_sql, " +
            " request_data:task_configuration_parameters AS task_configuration_parameters, " +
            " request_data:transcoding_parameters AS transcoding_parameters, " +
            " request_data:run_id AS run_id " +
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " +
            " WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";

            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_QUESTION_RUN', 'PENDING']
            });

            var rs = stmt.execute();
            var newQuestionRunParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var resultTable = rs.getColumnValue(3);
                var resultTableDDL = rs.getColumnValue(4);
                var accounts = rs.getColumnValue(5);
                var accountNames = rs.getColumnValue(6);
                var organizationNames = rs.getColumnValue(7);
                var computeAccountId = rs.getColumnValue(8);
                var statementHash = rs.getColumnValue(9);
                var query = rs.getColumnValue(10);
                var procedureSQL = rs.getColumnValue(11);
                var taskConfigurationParameters = rs.getColumnValue(12);
                var transcodingParameters = rs.getColumnValue(13);
                var runId = rs.getColumnValue(14);

                newQuestionRunParams.push({
                    'requestID' : requestID,
                    'cleanRoomID' : cleanRoomID,
                    'resultTable' : resultTable,
                    'resultTableDDL' : resultTableDDL,
                    'accounts' : accounts,
                    'accountNames': accountNames,
                    'organizationNames': organizationNames,
                    'computeAccountId': computeAccountId,
                    'statementHash': statementHash,
                    'query' : query,
                    'procedureSQL' : procedureSQL,
                    'taskConfigurationParameters': taskConfigurationParameters,
                    'transcodingParameters': transcodingParameters,
                    'runId': runId
                })
                snowflake.execute({
                        sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                        binds: ["IN_PROGRESS", requestID]
                });
            }

            for (var i = 0; i < newQuestionRunParams.length; i++) {
                // Create new warehouse and task config
                var crqr_request_id = newQuestionRunParams[i]['requestID'];
                var sanitized_request_id = crqr_request_id.replace(/-/g, '').toUpperCase();
                var HABU_QUESTION_RUN_ROOT_TASK_NAME = "HABU_" + sanitized_request_id + "_ROOT_TASK";
                var HABU_QUESTION_RUN_FINALIZE_TASK_NAME = "HABU_" + sanitized_request_id + "_FINALIZE_TASK";

                // Retrieve passed task and warehouse configuration
                var task_configuration_parameters = JSON.parse(newQuestionRunParams[i]['taskConfigurationParameters']);
                var HABU_WAREHOUSE_NAME = task_configuration_parameters.warehouseName;
                // Logging the WH used for the run
                logStatementWithRequestID(`Using Warehouse ${HABU_WAREHOUSE_NAME} to serve to serve requestID: ${crqr_request_id}`, crqr_request_id)


                // Get transcoding parameters if exists
                let updatedTranscodingViewSQLs = '', updatedDropTranscodingViewSQLs = '', updatedFetchTranscodingErrorLogsSqls = '', updatedFetchTranscodingErrorLogsStatementHash = '', updatedFetchTranscodingMetricsLogsSqls ='', updatedFetchTranscodingMetricsStatementHash = '';
                if (newQuestionRunParams[i]['transcodingParameters'] !== null && newQuestionRunParams[i]['transcodingParameters'] !== "") {
                    logStatementWithRequestID(`Transcoding enabled for request ${crqr_request_id}`, crqr_request_id);
                     var transcoding_parameters = JSON.parse(newQuestionRunParams[i]['transcodingParameters']);
                     updatedTranscodingViewSQLs = transcoding_parameters.transcoding_view_sqls === null ? '' : escapeForSqlLiteral(transcoding_parameters.transcoding_view_sqls);
                     updatedDropTranscodingViewSQLs = transcoding_parameters.drop_transcoding_view_sqls === null ? '' : escapeForSqlLiteral(transcoding_parameters.drop_transcoding_view_sqls);

                    if (transcoding_parameters.fetch_transcoding_error_logs_sqls != null) {
                        updatedFetchTranscodingErrorLogsSqls = transcoding_parameters.fetch_transcoding_error_logs_sqls === null ? '' : escapeForSqlLiteral(transcoding_parameters.fetch_transcoding_error_logs_sqls);
                        updatedFetchTranscodingErrorLogsStatementHash = transcoding_parameters.fetch_transcoding_error_logs_statement_hash === null ? '' : escapeForSqlLiteral(transcoding_parameters.fetch_transcoding_error_logs_statement_hash);
                    }
                    if (transcoding_parameters.fetch_transcoding_metrics_logs_sqls != null) {
                         updatedFetchTranscodingMetricsLogsSqls = transcoding_parameters.fetch_transcoding_metrics_logs_sqls === null ? '' : escapeForSqlLiteral(transcoding_parameters.fetch_transcoding_metrics_logs_sqls);
                         updatedFetchTranscodingMetricsStatementHash = transcoding_parameters.fetch_transcoding_metrics_statement_hash === null ? '' : escapeForSqlLiteral(transcoding_parameters.fetch_transcoding_metrics_statement_hash);
                    }

                }

                // Create & execute root CRQ run task while escaping single quotes for query
                var questionRunParam = newQuestionRunParams[i];
                var escapedResultTable = escapeForSqlLiteral(questionRunParam.resultTable);
                var escapedResultTableDDL = escapeForSqlLiteral(questionRunParam.resultTableDDL);
                var escapedQuery = escapeForSqlLiteral(questionRunParam.query);
                var updatedProcedureSQL = questionRunParam.procedureSQL === null ? '' : escapeForSqlLiteral(questionRunParam.procedureSQL);
                var runId = escapeForSqlLiteral(questionRunParam.runId);

                var new_question_runs_root_task_sql = `CREATE OR REPLACE TASK CLEAN_ROOM.${HABU_QUESTION_RUN_ROOT_TASK_NAME} \
                                                   WAREHOUSE = ${HABU_WAREHOUSE_NAME} \
                                                   USER_TASK_TIMEOUT_MS = ${task_configuration_parameters.taskTimeout} \
                                                   AS CALL CLEAN_ROOM.ADD_NEW_QUESTION_RUN(
                                                    '${questionRunParam.requestID}',
                                                    '${questionRunParam.cleanRoomID}',
                                                    '${escapedResultTable}',
                                                    '${escapedResultTableDDL}',
                                                    '${questionRunParam.accounts}',
                                                    '${questionRunParam.accountNames}',
                                                    '${questionRunParam.organizationNames}',
                                                    '${questionRunParam.computeAccountId}',
                                                    '${questionRunParam.statementHash}',
                                                    '${escapedQuery}',
                                                    '${updatedProcedureSQL}',
                                                    '${updatedTranscodingViewSQLs}',
                                                    '${updatedFetchTranscodingErrorLogsSqls}',
                                                    '${updatedFetchTranscodingErrorLogsStatementHash}',
                                                    '${updatedFetchTranscodingMetricsLogsSqls}',
                                                    '${updatedFetchTranscodingMetricsStatementHash}',
                                                    '${runId}'
                                               );`;

                snowflake.execute({ sqlText: new_question_runs_root_task_sql });

                // Create and execute finalizer task for root task
                var new_question_runs_finalize_task = `CREATE OR REPLACE TASK CLEAN_ROOM.${HABU_QUESTION_RUN_FINALIZE_TASK_NAME}
                                                       WAREHOUSE = ${HABU_WAREHOUSE_NAME}
                                                       FINALIZE = ${HABU_QUESTION_RUN_ROOT_TASK_NAME}
                                                       AS
                                                           BEGIN
                                                               CALL CLEAN_ROOM.DROP_TRANSCODING_VIEWS('${questionRunParam.requestID}','${updatedDropTranscodingViewSQLs}');
                                                               ALTER TASK ${HABU_QUESTION_RUN_FINALIZE_TASK_NAME} SUSPEND;
                                                               DROP TASK IF EXISTS ${HABU_QUESTION_RUN_ROOT_TASK_NAME};
                                                               DROP TASK IF EXISTS ${HABU_QUESTION_RUN_FINALIZE_TASK_NAME};
                                                           END
                                                       ;`;
                snowflake.execute({ sqlText: new_question_runs_finalize_task });

                // Resume finalizer task and execute root task
                snowflake.execute({ sqlText: "ALTER TASK CLEAN_ROOM." + HABU_QUESTION_RUN_FINALIZE_TASK_NAME + " RESUME" });
                snowflake.execute({ sqlText: "EXECUTE TASK CLEAN_ROOM." + HABU_QUESTION_RUN_ROOT_TASK_NAME });
            }
            result = "SUCCESS";
        } catch (err) {

            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, "", Object.keys(this)[0]
                ]
            });
            var res = stmt.execute();
        }
        return result;
	$$;

CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_QUESTION_RUN(REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, RESULT_TABLE VARCHAR, RESULT_TABLE_DDL VARCHAR, ACCOUNTS_INPUT VARCHAR, ACCOUNT_NAMES_INPUT VARCHAR, ORG_NAMES_INPUT VARCHAR, COMPUTE_ACCOUNT_ID VARCHAR, STATEMENT_HASH VARCHAR, QUESTION_RUN_QUERY VARCHAR, PROCEDURE_SQL VARCHAR, TRANSCODING_VIEW_SQLS VARCHAR, FETCH_TRANSCODING_ERROR_LOGS_SQLS VARCHAR, FETCH_TRANSCODING_ERROR_LOGS_STATEMENT_HASH VARCHAR, FETCH_TRANSCODING_METRICS_LOGS_SQLS VARCHAR, FETCH_TRANSCODING_METRICS_STATEMENT_HASH VARCHAR, RUN_ID VARCHAR)
	returns string
	language javascript
	execute as owner as
	$$
       // Function for checking Valid JSON String or not.

        function isValidJSON(jsonString) {
            try {
                var o = JSON.parse(jsonString);
                if (o && typeof o === "object") {
                    return o;
                }
            }
            catch (e) { }
            return null;
        }

        // Install the New question run stored procedure

        try {

            var rs = snowflake.execute({sqlText: "SELECT CURRENT_WAREHOUSE()"});
            rs.next();
            var warehouse_used = rs.getColumnValue(1);

            msg = `Executing the question run report request using warehouse size - ${warehouse_used}`
            snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                binds:[msg, REQUEST_ID, Object.keys(this)[0]]
            }).execute();

            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();

            var habuShareDb = "HABU_CR_" + sf_clean_room_id + "_HABU_SHARE"

            snowflake.execute({
                sqlText: RESULT_TABLE_DDL
            });

            snowflake.execute({
                sqlText: "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM_RUN_RESULTS." + RESULT_TABLE + " TO SHARE " + habuShareDb
            });

            if ((ACCOUNTS_INPUT != null && ACCOUNTS_INPUT.trim().length != 0) &&
                (ACCOUNT_NAMES_INPUT != null && ACCOUNT_NAMES_INPUT.trim().length != 0) &&
                (ORG_NAMES_INPUT != null && ORG_NAMES_INPUT.trim().length != 0)
                ) {
                ACCOUNTS = ACCOUNTS_INPUT.split(",");
                ACCOUNT_NAMES = ACCOUNT_NAMES_INPUT.split(",");
                ORG_NAMES = ORG_NAMES_INPUT.split(",");
                for (var i = 0; i < ACCOUNTS.length; i++) {
                    var partnerShare = "HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
                    var partnerShareDb = "HABU_CR_" + ACCOUNTS[i] + "_" + sf_clean_room_id + "_PARTNER_SHARE_DB"
                    var shareName = ORG_NAMES[i] + "." + ACCOUNT_NAMES[i] + "." + partnerShare

                    snowflake.execute({
                        sqlText: "CREATE DATABASE IF NOT EXISTS " + partnerShareDb + " FROM SHARE " + shareName + " COMMENT = 'HABU_" + ACCOUNTS[i] + "'"
                    });

                    snowflake.execute({
                        sqlText: "GRANT IMPORTED PRIVILEGES ON DATABASE " + partnerShareDb + " TO ROLE ACCOUNTADMIN"
                    })
                    snowflake.execute({
                        sqlText: "GRANT IMPORTED PRIVILEGES ON DATABASE " + partnerShareDb + " TO ROLE SYSADMIN"
                    });
                }
            }

            // Transcoding views can only be generated once the partner share has been generated
            if (TRANSCODING_VIEW_SQLS != null && TRANSCODING_VIEW_SQLS.trim().length != 0) {
                let transcodedViewSqls = JSON.parse(TRANSCODING_VIEW_SQLS);
                for (var i = 0; i < transcodedViewSqls.length; i++) {
                    snowflake.execute({sqlText: transcodedViewSqls[i]});
                }
            }

            // Install procedure if exists
            if (PROCEDURE_SQL != null && PROCEDURE_SQL.trim().length != 0) {
                snowflake.execute({sqlText: PROCEDURE_SQL});
                // adding current session into statement_hash to allow own account queries
                snowflake.execute({
                    sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) select  '" + COMPUTE_ACCOUNT_ID + "','" + CLEAN_ROOM_ID + "', SHA2(current_session())"
                })
            } else {
                snowflake.execute({
                    sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) VALUES (:1, :2, :3)",
                    binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH]
                })
            }

            // Check and run insert into allowed statements for statement hashes for transcoding metrics
            if (FETCH_TRANSCODING_ERROR_LOGS_STATEMENT_HASH != null && FETCH_TRANSCODING_ERROR_LOGS_STATEMENT_HASH.trim().length != 0) {
                let transcodingErrorHashes = FETCH_TRANSCODING_ERROR_LOGS_STATEMENT_HASH.split("|");
                for (var i = 0; i < transcodingErrorHashes.length; i++) {
                    snowflake.execute({
                        sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) VALUES (:1, :2, :3)",
                        binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, transcodingErrorHashes[i]]
                    })
                }
            }

            // Check and run insert into allowed statements for statement hashes for transcoding metrics
            if (FETCH_TRANSCODING_METRICS_STATEMENT_HASH != null && FETCH_TRANSCODING_METRICS_STATEMENT_HASH.trim().length != 0) {
                let transcodingMetricsHashes = FETCH_TRANSCODING_METRICS_STATEMENT_HASH.split("|");
                for (var i = 0; i < transcodingMetricsHashes.length; i++) {
                    snowflake.execute({
                        sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) VALUES (:1, :2, :3)",
                        binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, transcodingMetricsHashes[i]]
                    })
                }
            }

            // Execute the actual question query
            var resultSet = snowflake.execute({sqlText: QUESTION_RUN_QUERY})
            qId = Object.keys(this)[0] + " - QUESTION_RUN_QUERY - Query ID: " + resultSet.getQueryId()

            while (resultSet.next()) {
                var runQueryResponse = resultSet.getColumnValueAsString(1);
                var json = isValidJSON(runQueryResponse);
                if (json != null) {
                    if (json.loggerMessage && json.loggerMessage.length != 0) {
                        opMsg = json.loggerMessage
                        snowflake.createStatement({
                            sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                            binds:[opMsg, REQUEST_ID, Object.keys(this)[0]]
                        }).execute();
                    }

                    // Throw Error if Message is not success for Python.
                    if (json.message && json.message != "SUCCESS") {
                        throw { code : json.code, message: json.message, state : json.state, stackTraceTxt : json.stackTraceTxt }
                    }

                }
            }

            snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                binds:[qId, REQUEST_ID, Object.keys(this)[0]]
            }).execute();

            errorMap = new Map();
            if (FETCH_TRANSCODING_ERROR_LOGS_SQLS != null && FETCH_TRANSCODING_ERROR_LOGS_SQLS.trim().length != 0) {
                let fetchErrorLogsSqls = FETCH_TRANSCODING_ERROR_LOGS_SQLS.split("|");
                for (var i = 0; i < fetchErrorLogsSqls.length; i++) {
                    var resultSet = snowflake.execute({
                        sqlText: fetchErrorLogsSqls[i]
                    });
                    while (resultSet.next()) {
                        datasetId = resultSet.getColumnValueAsString('DATASET_ID');
                        errorMessage = resultSet.getColumnValueAsString('ERROR_MESSAGE');
                        if (!errorMap.has(datasetId)) {
                            errorMap.set(datasetId, []);  // Initialize array if datasetId is not present
                        }
                        errorMap.get(datasetId).push(errorMessage);
                    }
                }
            }

            metricsMap = new Map();
            if (FETCH_TRANSCODING_METRICS_LOGS_SQLS != null && FETCH_TRANSCODING_METRICS_LOGS_SQLS.trim().length != 0) {
                let fetchMetricsLogsSqls = FETCH_TRANSCODING_METRICS_LOGS_SQLS.split("|");
                for (var i = 0; i < fetchMetricsLogsSqls.length; i++) {
                    var resultSet = snowflake.execute({
                        sqlText: fetchMetricsLogsSqls[i]}
                    );
                    while (resultSet.next()) {
                        datasetId = resultSet.getColumnValueAsString('DATASET_ID');
                        var row = {
                            totalCount: resultSet.getColumnValueAsString('TOTAL_COUNT'),
                            successCount: resultSet.getColumnValueAsString('SUCCESS_COUNT'),
                            errorCount: resultSet.getColumnValueAsString('ERROR_COUNT')
                        };
                        metricsMap.set(datasetId, row);
                    }
                }
            }


            if (errorMap.size !== 0 || metricsMap.size !== 0) {
                // Step 1: Create a container for the result
                finalResult = {};

                // Step 2: Convert Map to plain JS object and assign to error_message
                finalResult.error_messages = Object.fromEntries(errorMap);
                finalResult.metrics = Object.fromEntries(metricsMap);
                finalResult.runId = RUN_ID;

                var updateMetricsSQLResponse = `UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS
                                                SET RESPONSE = :1
                                                WHERE ID = '${REQUEST_ID}'`;

                snowflake.execute({sqlText: updateMetricsSQLResponse, binds: [JSON.stringify(finalResult)]});
            }

            // Delete the allowed statement for the current session
            if (PROCEDURE_SQL != null && PROCEDURE_SQL.trim().length != 0) {
                snowflake.execute({
                    sqlText: "DELETE FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS where ACCOUNT_ID = :1 and CLEAN_ROOM_ID = :2 and STATEMENT_HASH = SHA2(current_session())",
                    binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID]
                })
            } else {
                snowflake.execute({
                    sqlText: "DELETE FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS where ACCOUNT_ID = :1 and CLEAN_ROOM_ID = :2 and STATEMENT_HASH = :3",
                    binds: [COMPUTE_ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH]
                })
            }

            result = "COMPLETE";
            msg = "New question run added successfully"
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, REQUEST_ID, Object.keys(this)[0]
                ]
            });
            msg = err.message
            var res = stmt.execute();
        } finally {
            snowflake.execute({
                sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                binds: [result, REQUEST_ID]
            });

            opMsg = Object.keys(this)[0] + " - OPERATION STATUS - " + result + " - Detail: " + msg
            snowflake.createStatement({
                sqlText: 'CALL CLEAN_ROOM.SP_LOGGER(:1, :2, :3)',
                binds:[opMsg, REQUEST_ID, Object.keys(this)[0]]
            }).execute();
        }
        return result;
	$$;

CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.DROP_TRANSCODING_VIEWS(REQUEST_ID VARCHAR, DROP_TRANSCODING_VIEW_SQLS VARCHAR)
    returns string
    language javascript
    execute as owner as
$$
    // Stored procedure to delete any views created during transcoding

    if (DROP_TRANSCODING_VIEW_SQLS != null && DROP_TRANSCODING_VIEW_SQLS.trim().length != 0) {
        let dropTranscodingViewSqls = JSON.parse(DROP_TRANSCODING_VIEW_SQLS);
        for (var i = 0; i < dropTranscodingViewSqls.length; i++) {
            snowflake.execute({sqlText: dropTranscodingViewSqls[i]});
        }
    }
    return "SUCCESS";
$$;

end;

