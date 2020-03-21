function getMousePos(event) {
    var e = event || window.event;
    var mouse = {'x':e.screenX,'y':screenY};
    return mouse;
}

var mouse_xPos;
var mouse_yPos;

// 桌面助手拖动
function domReady(fn){
    if(document.addEventListener){
        document.addEventListener('DOMContentLoaded',function(){
            fn&&fn();//处理事情
        },false);
    }else{
        /*监控资源情况，ie8及以下不支持addEventListener*/
        document.onreadystatechange=function(){
            /*dom加载完成的时候*/
            if(document.readyState=='complete'){
                fn&&fn();//处理事情
            }
        };
    }
}
//事件绑定兼容
function addEvent(obj,oEvn,fn){
    if(obj.addEventListener){
        obj.addEventListener(oEvn,fn,false);
    }else{
        obj.attachEvent('on'+oEvn,fn);
    }
}
//解除事件绑定
function removeEvent(obj,oEvn,fn){
    if(obj.removeEventListener){
        obj.removeEventListener(oEvn,fn,false);
    }else{
        obj.detachEvent('on'+oEvn,fn);
    }
}
domReady(function(){
    var oBox = document.getElementById("bidiu");
    function down(ev){
        mouse_xPos = getMousePos(event).x;
        mouse_yPos = getMousePos(event).y;
        timeFlag = false;
        hideBidiuTalk();
        var oEvent = ev || event;
        var disX=oEvent.clientX-oBox.offsetLeft;
        var disY=oEvent.clientY-oBox.offsetTop;
        function move(ev){
            var oEvent=ev||event;
            var l=oEvent.clientX-disX;
            var t=oEvent.clientY-disY;
            if(l<0){
                l=0;
            }
            if(l>document.documentElement.clientWidth-oBox.offsetWidth){
                l=document.documentElement.clientWidth-oBox.offsetWidth;
            }
            if(t<0){
                t=0;
            }
            if(t>document.documentElement.clientHeight-oBox.offsetHeight){
                t=document.documentElement.clientHeight-oBox.offsetHeight;
            }
            oBox.style.left=l+'px';
            oBox.style.top=t+'px';
        }
        function up(){
            if(getMousePos(event).x === mouse_xPos && getMousePos(event).y === mouse_yPos){
                showOptionGuide();
            }
            var bidiu_left = $("#bidiu").css("left").split("px")[0];
            var bidiu_top = $("#bidiu").css("top").split("px")[0];
            bidiu_left = parseInt(bidiu_left) - 75;
            bidiu_top = parseInt(bidiu_top) - 60;
            $("#bidiu_talk").css("left", bidiu_left + "px");
            $("#bidiu_talk").css("top", bidiu_top + "px");
            timeFlag = true;
            removeEvent(document,"mousemove",move);
            removeEvent(document,"mouseup",up);
            //释放捕获
            oBox.releaseCapture && oBox.releaseCapture();
        }
        addEvent(document,"mousemove",move);
        addEvent(document,"mouseup",up);
        //设置捕获
        oBox.setCapture && oBox.setCapture();
        //阻止浏览器默认事件
        oEvent.preventDefault && oEvent.preventDefault();
        return false;
    }
    addEvent(oBox,"mousedown",down);
});


setTimeout("showBidiuTalk()",2000);
var timeFlag = true;
function showBidiuTalk() {
    if(timeFlag){
        $("#bidiu_talk").show();
        setTimeout("hideBidiuTalk()",3000);
    }
}

function hideBidiuTalk() {
    $("#bidiu_talk").hide();
    if(timeFlag){
        var time = Math.floor((Math.random() * 7 + 3) * 1000);
        setTimeout("showBidiuTalk()", time);
        var text = changeTalk();
        $("#bidiu_talk").html(text);
    }
}

function changeTalk() {
    var teacher_text = ["点我查看操作指南哦！", "我是比丢，你的操作助手~", "我可以被拖动哦，试试吧", "Hello World!", "点击我可以修改个人信息哦"];
    var techer_index;
    var student_text = ["点我查看操作指南哦！", "我是比丢，你的操作助手~", "我可以被拖动哦，试试吧", "快来学习吧", "Hello World!", "点击我可以修改个人信息哦"];
    var student_index;
    var text;
    // if(user !== null && user !== "" && user !== undefined){  // 如果是教师角色
    //     techer_index = Math.round(Math.random() * 6);
    //     text = teacher_text[techer_index];
    // }else{ // 如果是学生角色
        student_index = Math.round(Math.random() * 7);
        text = student_text[student_index];
    // }
    return text;
}

function showOptionGuide(){
    // 打开对话框
}

function closeOptionGuide() {
    // 关闭对话框
}