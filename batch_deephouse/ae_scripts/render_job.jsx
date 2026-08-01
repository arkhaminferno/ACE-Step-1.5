/**
 * Apply one HAYA render job to Haya songs.aep.
 * Sets Arabic title, swaps background still, imports audio, extends duration.
 */

runScript(function () {
    function namesMatch(a, b) {
        return String(a).toLowerCase().replace(/\s+$/, "") === String(b).toLowerCase().replace(/\s+$/, "");
    }

    function findRootComp(name) {
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (item instanceof CompItem && namesMatch(item.name, name)) {
                return item;
            }
        }
        return null;
    }

    function findNestedComp(name, comp) {
        if (!comp) {
            return null;
        }
        for (var i = 1; i <= comp.numLayers; i++) {
            var source = comp.layer(i).source;
            if (source instanceof CompItem) {
                if (namesMatch(source.name, name)) {
                    return source;
                }
                var nested = findNestedComp(name, source);
                if (nested) {
                    return nested;
                }
            }
        }
        return null;
    }

    function resolveEditComp(job, mainComp) {
        var names = [job.edit_comp];
        if (job.edit_comp_fallbacks) {
            for (var i = 0; i < job.edit_comp_fallbacks.length; i++) {
                names.push(job.edit_comp_fallbacks[i]);
            }
        }
        for (var n = 0; n < names.length; n++) {
            var root = findRootComp(names[n]);
            if (root) {
                return root;
            }
            var nested = findNestedComp(names[n], mainComp);
            if (nested) {
                return nested;
            }
        }
        return null;
    }

    // Keep the AEP typeface (Alhambra). Only swap the string.
    // Template title is Latin \"yalil\" in Alhambra — not Arabic script.
    function setTextLayerKeepFont(layer, textValue) {
        var textProp = layer.property("ADBE Text Properties").property("ADBE Text Document");
        var textDoc = textProp.value;
        var prev = String(textDoc.text || "");
        if (prev === String(textValue)) {
            logLine("TITLE UNCHANGED (font preserved): " + prev);
            return;
        }
        var font = textDoc.font;
        var fontSize = textDoc.fontSize;
        var applyFill = textDoc.applyFill;
        var fillColor = null;
        if (applyFill) {
            fillColor = textDoc.fillColor;
        }
        var applyStroke = textDoc.applyStroke;
        // Never read strokeColor when stroke is off — AE throws:
        // "Can't get color, this text has no stroke."
        var strokeColor = null;
        var strokeWidth = 0;
        if (applyStroke) {
            strokeColor = textDoc.strokeColor;
            strokeWidth = textDoc.strokeWidth;
        }
        var justification = textDoc.justification;
        var tracking = textDoc.tracking;
        var fauxBold = textDoc.fauxBold;
        var fauxItalic = textDoc.fauxItalic;

        textDoc.text = textValue;
        var keepFont = font || "Alhambra";
        try {
            textDoc.font = keepFont;
        } catch (fontErr) {
            try {
                textDoc.font = "Alhambra";
            } catch (ignore) {}
        }
        textDoc.fontSize = fontSize;
        textDoc.applyFill = applyFill;
        if (applyFill && fillColor) {
            textDoc.fillColor = fillColor;
        }
        textDoc.applyStroke = applyStroke;
        if (applyStroke && strokeColor) {
            textDoc.strokeColor = strokeColor;
            textDoc.strokeWidth = strokeWidth;
        }
        textDoc.justification = justification;
        textDoc.tracking = tracking;
        textDoc.fauxBold = fauxBold;
        textDoc.fauxItalic = fauxItalic;
        textProp.setValue(textDoc);
        logLine("TITLE FONT KEPT: " + keepFont + " | " + prev + " -> " + textValue);
    }

    function isTitleLayer(layer, job) {
        var lower = layer.name.toLowerCase().replace(/\s+$/, "");
        var target = String(job.title_text_layer || "yalil").toLowerCase();
        return lower === target || lower.indexOf("yalil") >= 0;
    }

    function replaceTitleText(editComp, job) {
        var target = null;
        for (var i = 1; i <= editComp.numLayers; i++) {
            var layer = editComp.layer(i);
            if (layer.property("ADBE Text Properties")) {
                if (isTitleLayer(layer, job) || !target) {
                    target = layer;
                }
            }
        }
        if (!target) {
            throw new Error("Title text layer not found in " + editComp.name);
        }
        // Reuse AEP Alhambra / styling; only change glyphs when the song differs.
        setTextLayerKeepFont(target, job.display_name);
    }

    function relinkMissingFootage(templateFile) {
        var assetsFolder = new Folder(templateFile.parent.fsName + "/assets");
        if (!assetsFolder.exists) {
            return;
        }
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (!(item instanceof FootageItem) || !item.file) {
                continue;
            }
            var candidate = new File(assetsFolder.fsName + "/" + item.file.name);
            if (candidate.exists) {
                try {
                    item.replace(candidate);
                } catch (ignore) {}
            }
        }
    }

    function replaceBackgroundStill(job) {
        var bgFile = new File(job.background_path);
        if (!bgFile.exists) {
            throw new Error("Background missing: " + job.background_path);
        }
        var bgName = bgFile.name.toLowerCase();
        var replaced = false;
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (!(item instanceof FootageItem) || !item.file) {
                continue;
            }
            var name = item.file.name.toLowerCase();
            // Swap the portrait still used by the "Replace image" layer.
            if (
                name.indexOf("bd4a5f15") >= 0 ||
                name === "hawa.png" ||
                name === "rouh.png" ||
                name === "ward.png" ||
                name === "shouf.png" ||
                name === "baid.png" ||
                name === "noor.png" ||
                name === bgName ||
                (name.indexOf(".png") >= 0 &&
                    name.indexOf("haya") < 0 &&
                    name.indexOf("copyright") < 0 &&
                    name.indexOf("citypng") < 0)
            ) {
                item.replace(bgFile);
                replaced = true;
                logLine("BG REPLACED: " + item.name + " -> " + bgFile.name);
                break;
            }
        }
        if (!replaced) {
            var imported = app.project.importFile(new ImportOptions(bgFile));
            logLine("BG IMPORTED (no existing still match): " + imported.name);
        }
    }

    function importAudio(job) {
        var audioFile = new File(job.mp3_path);
        if (!audioFile.exists) {
            throw new Error("Missing audio: " + job.mp3_path);
        }
        var importOptions = new ImportOptions(audioFile);
        importOptions.importAs = ImportAsType.FOOTAGE;
        return app.project.importFile(importOptions);
    }

    function removeOldAudioLayers(comp) {
        for (var i = comp.numLayers; i >= 1; i--) {
            var layer = comp.layer(i);
            if (layer.hasAudio && !layer.hasVideo) {
                layer.remove();
            }
        }
    }

    function frameSafeDuration(comp, durationSec) {
        var frameDur = 1.0 / comp.frameRate;
        var frames = Math.max(1, Math.floor(durationSec * comp.frameRate));
        return frames * frameDur;
    }

    function setWorkArea(comp, durationSec) {
        var frameDur = 1.0 / comp.frameRate;
        var safeDur = frameSafeDuration(comp, durationSec);
        comp.duration = safeDur;
        comp.workAreaStart = 0;
        var workDur = safeDur - frameDur;
        if (workDur < frameDur) {
            workDur = frameDur;
        }
        comp.workAreaDuration = workDur;
        return safeDur;
    }

    function enableLoopOnVideoLayer(layer, safeDur) {
        if (!layer.source || !(layer.source instanceof FootageItem)) {
            return;
        }
        if (layer.source.mainSource && layer.source.mainSource.isStill) {
            layer.outPoint = safeDur;
            return;
        }
        try {
            layer.timeRemapEnabled = true;
            var remap = layer.property("ADBE Time Remapping");
            if (remap) {
                remap.expression = "loopOut();";
            }
            layer.outPoint = safeDur;
        } catch (ignore) {
            layer.outPoint = safeDur;
        }
    }

    function extendCompLayers(comp, safeDur) {
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            if (layer.source && layer.source instanceof CompItem) {
                layer.source.duration = safeDur;
                extendCompLayers(layer.source, safeDur);
                layer.outPoint = safeDur;
            } else {
                enableLoopOnVideoLayer(layer, safeDur);
            }
        }
    }

    function fitMainComp(mainComp, editComp, audioFootage, durationSec) {
        removeOldAudioLayers(mainComp);
        var audioLayer = mainComp.layers.add(audioFootage);
        audioLayer.startTime = 0;
        var safeDur = frameSafeDuration(mainComp, durationSec);
        editComp.duration = safeDur;
        extendCompLayers(editComp, safeDur);
        extendCompLayers(mainComp, safeDur);
        audioLayer.outPoint = safeDur;
        setWorkArea(mainComp, durationSec);
        app.project.workAreaStart = 0;
        app.project.workAreaDuration = mainComp.workAreaDuration;
    }

    var job = HAYA_JOB;
    var templateFile = new File(job.template_aep);
    if (!templateFile.exists) {
        throw new Error("Template missing: " + job.template_aep);
    }

    logLine("OPEN: " + templateFile.fsName);
    app.open(templateFile);
    relinkMissingFootage(templateFile);
    replaceBackgroundStill(job);
    app.beginUndoGroup("HAYA render " + job.slug);

    var mainComp = findRootComp(job.render_comp);
    if (!mainComp) {
        throw new Error("Missing render comp: " + job.render_comp);
    }
    var editComp = resolveEditComp(job, mainComp);
    if (!editComp) {
        throw new Error("Missing edit comp. Tried: " + job.edit_comp);
    }

    replaceTitleText(editComp, job);

    var audioFootage = importAudio(job);
    fitMainComp(mainComp, editComp, audioFootage, job.duration_sec);

    app.project.save(new File(job.project_path));
    app.endUndoGroup();
    logLine("SAVED: " + job.project_path);
});
