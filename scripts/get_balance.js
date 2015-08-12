#!/usr/bin/env casperjs --ssl-protocol=any
var casper = require('casper').create({
	verbose: false,
    logLevel: "info"
});

var url="https://www.schwab.com/public/schwab/client_home";
var username="";
var password="";

casper.start(url, function() {

	console.log("Checking login status @ " + url);

	this.waitForSelector("form[name='SignonForm']", function() { 
		this.fill('form#login', {
			'SignonAccountNumber': username,
			'SignonPassword':  password,
		}, true);
	});
});

casper.then(function() {

	if (/YES/.test(this.getCurrentUrl())) {
		this.thenOpen(this.getCurrentUrl(), function() {
			this.echo("Your balance: " + this.getHTML('#ctl00_wpm_ac_ac_rba_ctl00_dsv'));
		});
	} else {
		this.echo("Looks like the login failed.");
        this.exit()
	}
    
});

casper.then(function(){
    this.echo('Logging out.')
    this.click('li.logout a');
});

casper.then(function(){
   this.echo('Back at ' + this.getCurrentUrl()) 
});

casper.run();
