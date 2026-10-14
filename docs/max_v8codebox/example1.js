function removeObjects() {
    var thisPatcher = this.patcher;
    var rnboObj = thisPatcher.getnamed("sousaFxRnbo");
    var rnboSubPatcher = rnboObj.subpatcher();

    var bindingsObj = rnboSubPatcher.getnamed("bindings");
    var bindingsSubPatcher = bindingsObj.subpatcher();

    var obj = bindingsSubPatcher.firstobject;
    var toRemove = [];

    while (obj) {
        var text = String(obj.boxtext);
        if (text.indexOf("p @file sendbind") === 0) {
            toRemove.push(obj);
        }
        obj = obj.nextobject;
    }

    for (var i = 0; i < toRemove.length; i++) {
        bindingsSubPatcher.remove(toRemove[i]);
    }

    post("Removed " + toRemove.length + " objects\n");
}