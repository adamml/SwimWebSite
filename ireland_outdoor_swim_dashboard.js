/**
 * Builds a swim dashboard for Ireland's beaches. Data from Environmental
 * Protection Agency, Marine Institute, Met Eireann.
 * 
 * ## License
 * 
 * ## Disclaimer
 * 
 */

/**
 * Takes the name of a county in Ireland and returns the Federal Information
 * Processing Standard (FIPS) code for that county.
 *
 * @param {string} county The county name as a string
 *
 * @returns {string} The FIPS code for county
 *
 * @throws Will throw an error if `county` is not a `string`
 * @throws Will throw an error if the county name is invalid
 *
 * @author adamml
 * @since 1.0
 *
 * @static
*/
function fipsCode(county) {
	var countyFIPS;
	if(typeof county === 'string' || county instanceof String){
		switch(county.toLowerCase()) {
			case "carlow": countyFIPS = "EI01"; break;
			case "cavan": countyFIPS = "EI02"; break;
			case "clare": countyFIPS = "EI03"; break;
			case "cork": countyFIPS = "EI04"; break;
			case "donegal": countyFIPS = "EI06"; break;
			case "dublin": countyFIPS = "EI07"; break;
			case "galway": countyFIPS = "EI10"; break;
			case "kerry": countyFIPS = "EI11"; break;
			case "kildare": countyFIPS = "EI12"; break;
			case "kilkenny": countyFIPS = "EI13"; break;
			case "laois": countyFIPS = "EI15"; break;
			case "leitrim": countyFIPS = "EI14"; break;
			case "limerick": countyFIPS = "EI16"; break;
			case "longford": countyFIPS = "EI18"; break;
			case "louth": countyFIPS = "EI19"; break;
			case "mayo": countyFIPS = "EI20"; break;
			case "meath": countyFIPS = "EI21"; break;
			case "monaghan": countyFIPS = "EI22"; break;
			case "offaly": countyFIPS = "EI23"; break;
			case "roscommon": countyFIPS = "EI24"; break;
			case "sligo": countyFIPS = "EI25"; break;
			case "tipperary": countyFIPS = "EI26"; break;
			case "waterford": countyFIPS = "EI27"; break;
			case "westmeath": countyFIPS = "EI29"; break;
			case "wexford": countyFIPS = "EI30"; break;
			case "wicklow": countyFIPS = "EI31"; break;
			default: throw 'Invalid county name'; break;
		}
		return countyFIPS;
	} else {
		throw 'Parameter: [county] is not a string...';
	}
}

/**
 * Defines a callback to the page with a new parameter when selected from the
 * dropdown
 * 
 * @param {*} beaches 
 */
function dropdown_callback(beaches){
    window.location.href = `${document.URL.split("?")[0]}?beach_id=${beaches.value}`;
}

 fetch('https://api.beaches.ie/odata/beaches')
    .then(res => res.json())
    .then(function(result){

        var beach_id;
        try {
            beach_id = document.URL.split("?beach_id=")[1];
        } catch (error) {
            beach_id = "IEWEBWC170_0000_0200";
        }

        if(beach_id == null){
            beach_id = "IEWEBWC170_0000_0200";
        }

        var dropdown = document.getElementById("beach");
        var option;
        
        result["value"].forEach(function(elem){
            option = document.createElement("option");
            option.setAttribute("value", `${elem["Code"]}`);
            option.appendChild(document.createTextNode(`${elem["Name"]}, County ${elem["CountyName"]}`));
            dropdown.appendChild(option);

            if(elem["Code"] == beach_id){
                // TODO: Add Blue Flag status
                document.getElementById("name_location").appendChild(document.createTextNode(`${elem["Name"]}, County ${elem["CountyName"]}`));
                if(elem["IsBlueFlag"]){
                    console.log("Blue flag");
                    document.getElementById("name_location").appendChild(document.createElement("span").appendChild(document.createTextNode(" flag")));
                }
                if(elem["HasRestrictionInPlace"]){
                    console.log("Restriction");
                    document.getElementById("name_location").appendChild(document.createElement("span").appendChild(document.createTextNode(" restriction")));
                }
                document.getElementById("lat_value").appendChild(document.createTextNode(String(elem["EtrsY"])));
                document.getElementById("lon_value").appendChild(document.createTextNode(String(elem["EtrsX"])));
                document.getElementById("water-quality-value").appendChild(document.createTextNode(String(elem["WaterQualityName"])));
                document.getElementById("last-water-quality-sample").appendChild(document.createTextNode(String(elem["LastSampleOn"]).split("T")[0]));
                document.getElementById("next-water-quality-sample").appendChild(document.createTextNode(String(elem["NextMonitoringDate"]).split("T")[0]));

                fetch(`https://www.met.ie/Open_Data/json/warning_${fipsCode(elem['CountyName'])}.json`)
                    .then(res => console.log(res.json()))

            }
        });
        return result;
    })
    .then(res => console.log(res));