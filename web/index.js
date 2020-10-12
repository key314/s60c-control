const tl_container = document.getElementsByClassName("tl_container")[0];

const get_tl_block_array = () => {
    const blocks = tl_container.getElementsByClassName("tl_block");
    return [].slice.call(blocks);
};

const ID_PREFIX = "block"
const add_timeline_block = () => {
    const blocks = get_tl_block_array();
    const nextnode = blocks.slice(-1)[0].cloneNode(true);
    nextnode.id = ID_PREFIX + blocks.length;
    tl_container.append(nextnode);
    document.getElementsByClassName("button_remove")[0].disabled = false;
};

const remove_timeline_block = () => {
    const blocks = get_tl_block_array();
    if (blocks.length > 1) {
        tl_container.removeChild(blocks.slice(-1)[0]);
    };
    if (blocks.length == 2) {
        document.getElementsByClassName("button_remove")[0].disabled = true;
    };
};

const get_fade_info = () => {
    let fades = [];
    get_tl_block_array().forEach(b => {
        const duration = (b.id == "initial_block") ? 1 : parseFloat(b.getElementsByClassName("duration")[0].value) * 1000;
        const intensity = parseFloat(b.getElementsByClassName("intensity")[0].value);
        const temperature = parseFloat(b.getElementsByClassName("temperature")[0].value);
        fades.push({"duration":duration, "intensity":intensity,"temperature":temperature});
    });
    return fades;
};

const reset_progressbars = () => {
    [].slice.call(tl_container.getElementsByClassName("complete")).forEach(node => {
        node.classList.remove("complete");
        if (node.classList.contains("progressbar")) {
            node.style.height = "0%";
        };
    });
};

const get_ipaddr = () => {
    return document.getElementById("ipaddress").value;
};

eel.expose(current_value_callback);
function current_value_callback(intensity, temperature) {
    console.log(intensity);
};

let current_progressbar = null;

eel.expose(progress_callback);
function progress_callback(percentage) {
    if (current_progressbar != null) {
        current_progressbar.style.height = Math.round(percentage) + "%";
    };
};

eel.expose(finish_callback);
function finish_callback(task_id) {
    let bl_array = get_tl_block_array();
    bl_array[task_id].getElementsByClassName("progressbar_bg")[0].classList.add("complete");
    bl_array[task_id].getElementsByClassName("progressbar")[0].style.height = "100%";
    if (task_id + 1 < bl_array.length) {
        current_progressbar = bl_array[task_id + 1].getElementsByClassName("progressbar")[0];
        current_progressbar.classList.add("complete");
    } else {
        document.getElementsByClassName("button_start")[0].disabled = false;
    }
};


const start_fade = () => {
    reset_progressbars();
    eel.start_fade(get_ipaddr(), get_fade_info());
    document.getElementsByClassName("button_start")[0].disabled = true;
};
