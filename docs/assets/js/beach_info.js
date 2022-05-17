function get_met_eireann_warnings(fips_code){
    fetch(`https://www.met.ie/Open_Data/json/warning_${fips_code}.json`)
        .then(res => res.json())
        .then(out => console.log(out));
}