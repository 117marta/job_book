function jobs_info(job_pk) {
    const jobsMoreInfo = document.getElementById('jobs-more-info-' + job_pk);
    if (jobsMoreInfo.style.display === "none") {
        jobsMoreInfo.style.display = "block";
    } else {
        jobsMoreInfo.style.display = "none";
    }
}


const formJobUpdate = document.getElementById('form-job-update')
function form_job_update_submit()  {
    formJobUpdate.submit();
}
