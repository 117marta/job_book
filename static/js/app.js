function jobs_info(job_pk) {
    const jobsMoreInfo = document.getElementById('jobs-more-info-' + job_pk);
    if (jobsMoreInfo.style.display === "none") {
        jobsMoreInfo.style.display = "block";
    } else {
        jobsMoreInfo.style.display = "none";
    }
}
