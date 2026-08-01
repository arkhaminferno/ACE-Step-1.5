/**
 * Shared helpers for HAYA AE automation scripts.
 */

function logLine(line) {
    $.writeln(line);
}

function appendLog(line) {
    logLine(line);
}

function loadJobFromPointer() {
    if (typeof HAYA_JOB !== "undefined" && HAYA_JOB) {
        return HAYA_JOB;
    }
    throw new Error("HAYA_JOB missing from bundled script");
}

function aeWorkDir() {
    if (typeof HAYA_WORK_DIR !== "undefined" && HAYA_WORK_DIR) {
        return HAYA_WORK_DIR;
    }
    return Folder.temp.fsName;
}

function writeTextFile(file, text) {
    file.open("w");
    file.write(String(text || ""));
    file.close();
}

function quitAfterEffects() {
    try {
        app.quit(SaveOptions.DONOTSAVECHANGES);
    } catch (ignore) {}
}

function runScript(mainFn) {
    try {
        mainFn();
    } catch (error) {
        var message = error && error.toString ? error.toString() : String(error);
        logLine("ERROR: " + message);
        alert(message);
        throw error;
    } finally {
        quitAfterEffects();
    }
}

function defaultTemplatePath() {
    return "";
}
