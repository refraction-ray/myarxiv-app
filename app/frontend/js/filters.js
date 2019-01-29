function datafromobj (obj) {
    return $.strftime(obj);
};
function datewithspace (v) {
    let [y, m, d] = v.split("-");
    return y + " " + m + " " + d;
};
export {
    datefromobj,
    datewithspace
};