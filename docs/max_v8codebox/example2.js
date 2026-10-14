function removeObjects() {
    var thisPatcher = this.patcher;
    var rnboObj = thisPatcher.getnamed("sousaFxRnbo");
    var subPatcher = rnboObj.subpatcher();

    var pattern = /^removeForRpi(\[\d+\])?$/;
    var obj = subPatcher.firstobject;
    var toRemove = [];

    while (obj) {
        if (pattern.test(obj.varname)) {
            toRemove.push(obj);
        }
        obj = obj.nextobject;
    }

    for (var i = 0; i < toRemove.length; i++) {
        subPatcher.remove(toRemove[i]);
    }

    post("Removed " + toRemove.length + " objects\n");
}