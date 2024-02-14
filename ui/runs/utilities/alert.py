def build_trace_alert(trace):
    return f'<div class="accordion accordion-flush mt-4"><div class="accordion-item">\
        <h2 class="accordion-header" id="flush-headingOne">\
        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" \
        style="background-color: transparent;" data-bs-target="#flush-collapseOne" \
        aria-expanded="false" aria-controls="flush-collapseOne">\
        Trace</button></h2><div id="flush-collapseOne" class="accordion-collapse collapse" \
        aria-labelledby="flush-headingOne" data-bs-parent="#accordionFlushExample">\
        <div class="accordion-body bg-white"><pre>{trace}</pre></div></div></div></div>'
