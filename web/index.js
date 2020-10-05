const tl_container = document.getElementsByClassName("tl_container")[0];

const get_tl_block_array = () => {
    const blocks = tl_container.getElementsByClassName("tl_block");
    return [].slice.call(blocks);
};

const add_timeline_block = () => {
    const blocks = get_tl_block_array();
    const nextnode = blocks.slice(-1)[0].cloneNode(true);
    nextnode.id = "block" + blocks.length;
    tl_container.append(nextnode);
};

const remove_timeline_block = () => {
    const blocks = get_tl_block_array();
    tl_container.removeChild(blocks.slice(-1)[0]);
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

const get_ipaddr = () => {
    return document.getElementById("ipaddress").value;
};


const start_fade = () => {
    eel.start_fade(get_ipaddr(), get_fade_info());
};

eel.expose(view_current_value);
const view_current_value = (intensity, temperature) => {
    console.log(intensity);
};
