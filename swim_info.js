import fetch from 'node-fetch';
import xml2js from 'xml2js';

import { DateTime } from 'luxon';

let id = 'IESWBWC090_0000_0300';

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
* Calculates if Daylight Savings are currently in operation or not
*
* @param {Date} d The date object to be checked for Daylight Savings
*
* @returns {Boolean} `true` if Daylight Saving Time is active, otherwise `false`
*
* @throws Will throw an error if `d` is not a `Date`
*
* @author adamml
* @since 1.0
*
* @static
*/
function isDST(d){
		if(typeof d === 'date' || d instanceof Date){
			const jan = new Date(d.getFullYear(), 0, 1);
			const jul = new Date(d.getFullYear(), 6, 1);
			return d.getTimezoneOffset() != Math.max(jan.getTimezoneOffset(), 
													jul.getTimezoneOffset());
		} else {
			throw 'Parameter: [d] is not a Date...';
		}
	}

function getTidePrediction(beachData, weatherWarning, weatherForecast){
	
	const beginDateTime = DateTime.now().toUTC().minus({days:1}).set({hour: 21, minute: 0, second: 0, millisecond: 0}).toISO();
	const endDateTime = DateTime.now().toUTC().plus({days:1}).set({hour: 3, minute: 0, second: 0, millisecond: 0}).toISO();
	
	fetch(`https://erddap.marine.ie/erddap/tabledap/IMI-TidePrediction_epa.json?time%2Csea_surface_height&time%3E=${beginDateTime}&time%3C=${endDateTime}&stationID=%22${beachData['Code']}_MODELLED%22`)
		.then(r => r.json())
		.then(r=> r['table']['rows'])
		.then(function(data){
			data.forEach(el => console.log(el));
			return data;
		})
		.catch(err => console.log(err))
}

function getWeatherForecast(beachData, weatherWarning){
	
	var now = Date.now();
	const nowD = new Date(now);
	const tomorrowD = new Date(now + (24*60*60*1000))
	const startDay = nowD.getDate().toString().padStart(2, '0');
	var endDay;
	const startMonth = (nowD.getMonth() + 1).toString().padStart(2, '0');
	var endMonth;
	const startYear = nowD.getFullYear().toString();
	var endYear;
	var startTime;
	var endTime;
	if(isDST(new Date(now))){
		endDay = tomorrowD.getDate().toString().padStart(2, '0');
		endMonth = (tomorrowD.getMonth() + 1).toString().padStart(2, '0');
		endYear = tomorrowD.getFullYear().toString();
		startTime = '01:00';
		endTime = '00:00';
	} else {
		endDay = nowD.getDate().toString().padStart(2, '0');
		endMonth = (nowD.getMonth() + 1).toString().padStart(2, '0');
		endYear = nowD.getFullYear().toString();
		startTime = '00:00';
		endTime = '23:00';
	}
	
	const beachLatStr = beachData['EtrsY'].toString();
	const beachLonStr = beachData['EtrsX'].toString();
	
	fetch(`http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat=${beachLatStr};long=${beachLonStr};from=${startYear}-${startMonth}-${startDay}T${startTime};to=${endYear}-${endMonth}-${endDay}T${endTime}`)
		.then(res => res.text())
		.then(function(data){
			xml2js.parseString(data, function (err, result) {
				getTidePrediction(beachData, weatherWarning, result);
			});
		})
		.catch(err => console.log(err))
}

function getWeatherWarning(beachData){
	fetch(`https://www.met.ie/Open_Data/json/warning_${beachData['fipsCode']}.json`)
		.then(res => res.json())
		.then(data => getWeatherForecast(beachData, data))
		.catch(err => console.log(err));
}

fetch(`https://api.beaches.ie/odata/beaches?$filter=Code%20eq%20%27${id}%27`)
	.then(res => res.json())
	.then(res => res['value'][0])
	.then(function(res){
		res['fipsCode'] = fipsCode(res['CountyName']);
		return res;
	})
	.then(data => getWeatherWarning(data))
	.catch(err => console.log(err));