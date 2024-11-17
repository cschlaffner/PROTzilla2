function selectRun(runName){
    document.getElementById('selectedRun').textContent = runName;
    document.getElementById('run_name_id').value = runName;
};

function deleteRun(runName){
    document.getElementById('delete_run_name_id').value = runName;
    document.getElementById('delete_run').submit();
};