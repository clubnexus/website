//Last updated by 1016 04/12/2005
//Global Hitbox Solution 1016 Version 1.0.9
//mlc fix for kids island
done = false;
b_domain = document.domain;
b_domain = b_domain.toString();
debug_mode = false;
debug_level=0;

vc_foo=window.location.search
if(vc_foo.indexOf("debug=true") != -1){
	debug_mode = true;
}
if(debug_mode==true && vc_foo.indexOf("&level") != -1){
	my_point = vc_foo.indexOf("&level") + 7;
	my_sub = vc_foo.substr(my_point);
	debug_level=parseInt(my_sub);
	//alert(debug_level);
}

function HB_MLC_Loop(arg){
	var hold = "";
	var mlcAr = arg.split("/");
	for(i=0;i<mlcAr.length;i++){
		if(mlcAr[i].indexOf(".") != -1){
		}
		else{
			hold += "/" + mlcAr[i];
		}
	}
	
	return hold;
	
}
function HB_MLC_Constructor(){
	var winLoc = window.location.toString();
	var winHost = window.location.host;
	var winHostLen = winHost.length;
	var winLocIndex = winLoc.indexOf(winHost) + winHostLen + 1;
	var winLocMLC = winLoc.substr(winLocIndex);
	var winLocMLC_Final = this.HB_MLC_Loop(winLocMLC);
	return winLocMLC_Final;
}


function HB_BrandTags(){
	whatBrand = false;
	try{
		if(opener)bCrumbLevel_1 = opener.bCrumbLevel_1;
	}catch(e){}
	try{
		if(bCrumbLevel_1 && window.location.toString().indexOf("movies.go.com") == -1){
			whatBrand = true;
		}
		
	}catch(e){whatBrand=false;}
	if(whatBrand){
		var foo = "/DB";
	}
	else{
		var foo = "/NB/";
	}
	return foo
}

function HB_GetDynDomain(){
	var this_domain = document.domain.toString();
	this_domain = this_domain
	return this_domain;
}

function HB_ParseBreadCrumb(arg){
			CIBreadCrumb = "bCrumbLevel_";


	this.x = 1;
	var myreturn = this.HB_BrandTags();
	if(myreturn == "/DB")myreturn += "/";
	if(myreturn == "/DB/"){
		
	do{
		if(this.x == 6) {
			this.done = true;			
		}				
		else {
			
			try{
				retValue = CIBreadCrumb + this.x;
				
				if(opener){
					if(opener.eval(retValue) != null && opener.eval(retValue) != "" && opener.eval(retValue) != "null"){
						myreturn += opener.eval(retValue) + "/";
					}
				}else{
					if(eval(retValue)!= null  && eval(retValue) != "" && eval(retValue) != "null"){
						myreturn += eval(retValue) + "/";
					}
				}
			}
			catch(e){
				
				try{
					retValue = CIBreadCrumb + this.x + "_text";
					if(opener){
						if(opener.eval(retValue) != null && opener.eval(retValue) != "" && opener.eval(retValue) != "null"){
							myreturn += opener.eval(retValue) + "/";
						}
					}else{
						if(eval(retValue) != null && eval(retValue) != "" && eval(retValue) != "null"){
							myreturn += eval(retValue) + "/";
						}
					}
				}
				catch(e){
					
				}
			}
				
			this.x++ 

		}
		

		}while (this.done != true);
		myreturn = HB_Chomp(myreturn);

		
	}
	else {
		if(arg){
			myreturn += arg;
		}
		else{
			dyn_domain = this.HB_GetDynDomain();
			dyn_domain = dyn_domain.replace(/.movies.go.com/,"");
			dyn_domain = dyn_domain.replace(/.go.com/,"");
			myreturn += dyn_domain;
		}
	}
		return (this.HB_ReplaceTool(myreturn));
}
function HB_Chomp(arg){
	var len = arg.length -1;
	return arg.substring(0,len);
}
function HB_ReplaceTool(arg){
	var str = arg;
	var newString = "";
	
	for(i=0;i<str.length;i++){
		str = str.replace(/ /,"+");
		hold = str.substring(i,i + 1);
		switch(hold){
			case "|" : 
			case "!" :
			case "#":
			case ":":
			case "$":
			case "%":
			case "&":
			case "'":
			case"\\":
			case ":":
			case "<":
			case "^":
			case ">":
			case "~":
			break;
			default : newString += hold;	
		}
		
	}
	str = newString;
	return str;
}
function HB_PlaceAccount(_args_){
	var foo = "";
	for(i=0;i<arguments.length;i++){
		foo += arguments[i] + ";"
	}
	foo = HB_Chomp(foo);
	this.account = foo;

}
function HB_WriteScript(){
	var port_type = window.location.protocol;
	var myHost = window.location.host;
	if(port_type.toLowerCase().indexOf("https") != -1){
		isAnS = "s";
		isACdn = "";
	}
	else {
		isAnS = "";
		isACdn = "hb.";
	}
	if(myHost.indexOf("disney") != -1 || myHost.indexOf("familyfun") != -1){
		whatDomain = "disney";
	}else{
		whatDomain = "global";
		//isACdn = "";
	}
	document.write('<script defer src="http'+isAnS+'://'+isACdn+ whatDomain+'.go.com/stat/hbx.js" type="text/javascript"></scr'+'ipt>');
}
function HB_RenderFunction(opt,typ,keywords,results,attr1,attr2,attr3,attr4)
{
	
	_hbEC=0,_hbE=new Array;function _hbEvent(a,b){b=_hbE[_hbEC++]=new Object();b._N=a;b._C=0;return b;}
	hbx=_hbEvent("pv");hbx.vpc="HBX0100u";hbx.gn="ehg-dig.hitbox.com";
	hbx.acct = this.account;
	hbx.mlc = this.mlc;
	hbx.pn = this.pn;	
	hbx.ci = this.ci;
	hbx.cpm = this.cmp;
	hbx.cmpn = this.cmpn;
	hbx.cp = this.cp;
	hbx.cpd = this.cpd;
	hbx.ctdef=this.ctdef;
	hbx.dcmp=this.dcmp;
	hbx.dcmpe=this.dcmpe;
	hbx.dcmpn=this.dcmpn;
	hbx.dcmpre=this.dcmpre;
	hbx.dlf=this.dlf;
	hbx.dft=this.dft;
	hbx.elf=this.elf;
	hbx.fnl=this.fnl;
	hbx.fv=this.fv;
	hbx.gp=this.gp;
	hbx.gpn=this.gpn;
	hbx.hcn=this.hcn; 
	hbx.hla=this.hla;
	hbx.hlt=this.hlt;
	hbx.hqsp=this.hqsp;
	hbx.hqsr=this.hqsr;
	hbx.hra=this.hra;
	hbx.hrf=this.hrf;
	hbx.hvc=this.hvc;
	hbx.lt=this.lt;
	hbx.pec=this.pec;
	hbx.pndef=this.pndef;
	hbx.seg=this.seg;
	if(this.onlyMedia)hbx.onlyMedia = this.onlyMedia;
	if(this.hc1)hbx.hc1=this.hc1;
	if(this.hc2)hbx.hc2=this.hc2;
	if(this.hc3)hbx.hc3=this.hc3;
	if(this.hc4)hbx.hc4=this.hc4;
	if(this.mlc.indexOf("CONTENT+CATEGORY") != -1) hbx.ctdef="full";
	if(typ){
		if(typ == "search"){
			ev1 = new _hbEvent(typ);
			ev1.keywords = keywords;
			ev1.results = results;
			if(attr1)ev1.attr1 = attr1;
			if(attr2)ev1.attr2 = attr2;
			if(attr3)ev1.attr3 = attr3;
			if(attr4)ev1.attr4 = attr4;
		}else{
			switch(opt){
				case 2 :
				ev2 = new _hbEvent(typ);
				ev2.keywords = keywords;
				ev2.results = results;
				if(attr1)ev2.attr1 = attr1;
				if(attr2)ev2.attr2 = attr2;
				if(attr3)ev2.attr3 = attr3;
				if(attr4)ev2.attr4 = attr4;
				break;
				case 3 :
				ev3 = new _hbEvent(typ);
				ev3.keywords = keywords;
				ev3.results = results;
				if(attr1)ev3.attr1 = attr1;
				if(attr2)ev3.attr2 = attr2;
				if(attr3)ev3.attr3 = attr3;
				if(attr4)ev3.attr4 = attr4;
				break;
				case 4:
				ev4 = new _hbEvent(typ);
				ev4.keywords = keywords;
				ev4.results = results;
				if(attr1)ev4.attr1 = attr1;
				if(attr2)ev4.attr2 = attr2;
				if(attr3)ev4.attr3 = attr3;
				if(attr4)ev4.attr4 = attr4;
				break;
			}
			

		}
	}
	if(debug_mode && debug_level == 3){
		alert("account has been changed");
		hbx.acct = "DM510925KJWE;DM510925KJWE;DM510925KJWE;DM510925KJWE";
	}
	if(debug_mode && debug_level==1){
		alert("MLC: " + this.mlc);
		alert("Page Name: " + this.pn);
	}
	else if(debug_mode && (debug_level==2 || debug_level==3)){
		debug_win = window.open("about:blank","debug_win");
		debug_win.document.write("<body><h2>Debug Window HBX</h2>")
		for(name in hbx){
			debug_win.document.write(name + ": " + hbx[name] + "<BR>");
			
		}
		debug_win.document.write("</body>");
		debug_win.document.close();
	}
	if(debug_mode && debug_level == 4){
		debug_win_other = window.open("","debug_win_other");
		debug_win_other.document.write("<body><h2>Degub Window ev1</h2>");
		for(name in ev1){
			debug_win_other.document.write(name + ": " + ev1[name] + "<br>");
		}
		debug_win_other.document.write("</body>");
		debug_win_other.document.close();
	}


		

	if(opt != "special"){
		this.HB_WriteScript();
		//alert("NW");
	}
	
}
function OutSide(opt,typ,keywords,results,attr1,attr2,attr3,attr4){
	_hbEC=0,_hbE=new Array;function _hbEvent(a,b){b=_hbE[_hbEC++]=new Object();b._N=a;b._C=0;return b;}
	this[opt] = new _hbEvent(typ);
	this[opt].keywords = keywords;
	this[opt].results = results;
	if(attr1)this[opt].attr1 = attr1;
	if(attr2)this[opt].attr2 = attr2;
	if(attr3)this[opt].attr3 = attr3;
	
}
function HB_PlaceName(arg){
	if(!arg){
		this.pn = "PUT+PAGE+NAME+HERE";
	}
	else{
		foo = HB_ReplaceTool(arg);
		this.pn = foo;
	}
}
function HB_AppendInformation(arg_mlc){
	var hold = "/";
	var inti = "";
	if(!arg_mlc){
		var protemp_mlc = this.first_mlc;
	}
	else{
		var protemp_mlc = arg_mlc;
	}
	return protemp_mlc;
	
}
// interface functions
function HB_ParseContentArray(){
	var myParse = "";
	
	for(i=0;i<contentTrackAr.length;i++){
		myParse += contentTrackAr[i] + ";";
	}
	myParse = this.HB_Chomp(myParse);
	return myParse;
}
//Flash functions
function Set_hbPageView(YourPageName,YourContentCategoryName,arrayInfo){
	if(YourContentCategoryName == true){
		contentTrackAr = arrayInfo;
		fromArray = this.HB_ParseContentArray();
		send_mlc = this.CI_Raw + this.HB_AppendInformation(contentTrackAr[0]);
		var complete_mlc = fromArray + ";" + send_mlc;
	}
	else{
		var send_mlc = this.CI_Raw + this.HB_AppendInformation(YourContentCategoryName) + "/flash";
		var complete_mlc = YourContentCategoryName + ";" + send_mlc;
	}
	_hbPageView(YourPageName,complete_mlc);
}
function Set_hbExitLink(YourExitLinkName){
	_hbExitLink(YourExitLinkName);
}
function Set_hbDownload(YourDownloadName){
	_hbDowload(YourDownloadName);
}

function Set_hbCampaign(YourCampaignID,YourPageName,YourContentCategoryName){
	_hbCampaign(YourCampaignID,YourPageName,YourContentCategoryName);
}
function Set_hbGoalPage(YourGoalPageCampaignID,YourPageName,YourContentCategoryName){
	_hbGoalPage(YourGoalPageCampaignID,YourPageName,YourContentCategoryName)
}
function Set_hbVisitorSeg(YourSegmentID,YourPageName,YourContentCategoryName){
	_hbVisitorSeg(YourSegmentID,YourPageName,YourContentCategoryName);
}
function Set_hbSet(AnyHBXGatewayVariable,AlternateValueOfVariable){
	_hbSet(AnyHBXGatewayVariable,AlternateValueOfVariable);
}
function Set_hbSend(){
	_hbSend();
	
}
function Set_hbLink(YourLinkID,YourLinkPosition){
	_hbLink(YourLinkID,YourLinkPosition)
}
//Custom Metric Code
function PlaceCustomMetric(val,res){
	switch(val){
		case "hc1":
		this.hc1 = res;
		try{hbx.hc1 = res;}catch(e){}
		break;
		case "hc2":
		this.hc2 = res;
		try{hbx.hc2 = res;}catch(e){}
		break;
		case "hc3":
		this.hc3 = res;
		try{hbx.hc3 = res;}catch(e){}
		break;
		case "hc4":
		this.hc4 = res;
		try{hbx.hc4 = res;}catch(e){}
		break;
	}
	return true;
}

function GetUrl(){
	winLoc = window.location.toString();
	winLoc = HH_ReplaceTool(winLoc);
	return winLoc;
	
}
function HH_ReplaceTool(arg){
	var str = arg;
	var newString = "";
	ind = str.indexOf("//");
	str = str.substr(ind + 2);
	for(i=0;i<str.length;i++){
		str = str.replace(/ /,"+");
		str = str.replace(/\//,"_");
		
	}
	for(i=0;i<str.length;i++)str=str.replace(/\./,"+");
	return str;
}
//Fixes Kids Island

	
function HB_CreateObject(the_mlc,nb_mlc){

	this.account = "";
	this.HB_GetDynDomain = HB_GetDynDomain;
	this.HB_ReplaceTool = HB_ReplaceTool;
	this.pn = "PUT+PAGE+NAME+HERE";
	this.HB_AppendInformation = HB_AppendInformation
	this.HB_PlaceAccount = HB_PlaceAccount
	this.HB_ParseBreadCrumb = HB_ParseBreadCrumb
	this.HB_Chomp = HB_Chomp;
	this.HB_BrandTags = HB_BrandTags;
	this.HB_render = HB_RenderFunction;
	this.HB_WriteScript = HB_WriteScript;
	this.HB_MLC_Constructor = HB_MLC_Constructor;
	this.HB_MLC_Loop = HB_MLC_Loop;
	this.HB_ParseContentArray = HB_ParseContentArray;
	//custom metrics
	this.PlaceCustomMetric = PlaceCustomMetric;
	//Flash Functions
	this.Set_hbPageView = Set_hbPageView
	this.Set_hbExitLink = Set_hbExitLink
	this.Set_hbDownload = Set_hbDownload
	this.Set_hbCampaign = Set_hbCampaign
	this.Set_hbGoalPage = Set_hbGoalPage
	this.Set_hbVisitorSeg = Set_hbVisitorSeg
	this.Set_hbSet = Set_hbSet;
	this.Set_hbSend = Set_hbSend;
	this.Set_hbLink = Set_hbLink;
	this.set_mlc = the_mlc;
	if(this.set_mlc.substring(0,1) != "/")this.set_mlc = "/" + this.set_mlc;
	this.first_mlc = this.HB_ReplaceTool(this.set_mlc);
	//End Flash Function
	if(nb_mlc){
		this.CI_Raw = this.HB_ParseBreadCrumb(nb_mlc);
	}
	else{
		this.CI_Raw = this.HB_ParseBreadCrumb();
	}
	this.combo_mlc = this.CI_Raw + this.HB_AppendInformation();
	this.mlc = this.first_mlc + ";" +  this.combo_mlc;
	if(this.mlc.indexOf("//") != -1)this.mlc = this.mlc.replace(/\/\//,"/");
	this.HB_PlaceName = HB_PlaceName;
	//alert(this.mlc);
	//campain variables
	this.ci="";
	this.cmp="";
	this.cmpn="";
	this.cp="null";
	this.cpd="";
	this.ctdef="full";
	this.dcmp="";
	this.dcmpe="";
	this.dcmpn="";
	this.dcmpre="";
	this.dlf="n";
	this.dft="n";
	this.elf="n";
	this.fnl="";
	this.fv="n";
	this.gp="";
	this.gpn="";
	this.hcn=""; 
	this.hla="";
	this.hlt="";
	this.hqsp="";
	this.hqsr="";
	this.hra="";
	this.hrf="";
	this.hvc="";
	this.lt="auto";
	this.pec="";
	this.pndef="title";
	this.seg="";
	this.hc1="";
	this.hc2="";
	this.hc3="";
	this.hc4="";
	this.onlyMedia = "";
	this.Init_ci=function(arg){this.ci=arg;}
	this.Init_cmp = function(arg){this.cmp=arg;}
	this.Init_cmpn = function(arg){this.cmpn=arg;}
	this.Init_cp = function(arg){this.cp=arg;}
	this.Init_cpd = function(arg){this.cpd=arg;}
	this.Init_ctdef=function(arg){this.ctdef=arg;}
	this.Init_dcmp = function(arg){this.dcmp=arg;}
	this.Init_dcmpe=function(arg){this.dcmpe=arg;}
	this.Init_dcmpn = function(arg){this.dcmpe=arg;}
	this.Init_dcmpre=function(arg){this.dcmpre=arg;}
	this.Init_dlf = function(arg){this.dlf = arg;}
	this.Init_dft = function(arg){this.dft = arg;}
	this.Init_elf = function(arg){this.elf = arg;}
	this.Init_fnl = function(arg){this.fnl=arg;}
	this.Init_fv = function(arg){this.fv = arg;}
	this.Init_gp = function(arg){this.gp=arg;}
	this.Init_gpn=function(arg){this.gpn=arg;}
	this.Init_hcn=function(arg){this.hcn=arg;}
	this.Init_hla=function(arg){this.hla=arg;}
	this.Init_hlt=function(arg){this.hlt=arg;}
	this.Init_hqsp=function(arg){this.hqsp=arg;}
	this.Init_hqsr=function(arg){this.hqsr=arg;}
	this.Init_hra = function(arg){this.hra=arg;}
	this.Init_hrf=function(arg){this.hrf=arg;}
	this.Init_hvc = function(arg){this.hvc=arg;}
	this.Init_lt = function(arg){this.lt = arg;}
	this.Init_onlyMedia = function(arg){this.onlyMedia=arg;}
	this.Init_pndef=function(arg){this.pndef=arg;}
	this.Init_pec = function(arg){this.pec=arg;}
	this.Init_seg = function(arg){this.seg=arg;}
	//degug code

	
}
	