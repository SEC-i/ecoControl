function get_timestamp(string) {
    return new Date(parseFloat(string) * 1000).getTime();
}