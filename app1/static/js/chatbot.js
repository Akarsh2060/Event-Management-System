document.addEventListener("DOMContentLoaded", function(){

const chatToggle = document.getElementById("chat-toggle");
const chatWindow = document.getElementById("chat-window");
const chatClose = document.getElementById("chat-close");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatMessages = document.getElementById("chat-messages");


// toggle chatbot
chatToggle.onclick = () => {

if(chatWindow.style.display === "flex"){
    chatWindow.style.display = "none";
}else{
    chatWindow.style.display = "flex";
}

};

chatClose.onclick = () => {
chatWindow.style.display = "none";
};


// send message
sendBtn.onclick = sendMessage;
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function sendMessage(){
    let message = userInput.value.trim();
    if(message === "") return;

    addMessage("You", message);
    userInput.value="";

    // Typing indicator
    const botMsg = showTyping();

    // knowledge logic
    const knowledge = [
        {
            keywords: ["account", "register", "signup", "login", "logged", "profile"],
            answer: "You're already part of the Zevents family! Since you're logged in, you can manage your bookings directly from 'My Events'."
        },
        {
            keywords: ["payment", "pay", "money", "price", "cost", "advance", "booking", "budget", "package"],
            answer: "We offer flexible pricing! A 25% advance is required to secure your date. We accept UPI, Cards, and Net Banking."
        },
        {
            keywords: ["wedding", "marriage", "varmala", "engagement", "reception"],
            answer: "Weddings are our specialty! From traditional Varmalas to grand receptions, we handle everything. Check our 'Diamond Plan' for luxury weddings."
        },
        {
            keywords: ["corporate", "conference", "meeting", "seminar", "workshop", "office"],
            answer: "We organize professional corporate events, including product launches and seminars, with full AV support and catering."
        },
        {
            keywords: ["birthday", "party", "anniversary", "celebration", "cake"],
            answer: "Let's celebrate! Whether it's a first birthday or a golden anniversary, we bring the fun with themed decor and great food."
        },
        {
            keywords: ["food", "catering", "menu", "vegetarian", "buffet", "dinner", "lunch"],
            answer: "Food is the heart of an event. Our plans include 'Per Head' catering options with a wide variety of cuisines."
        },
        {
            keywords: ["decor", "decoration", "flowers", "theme", "lighting", "stage"],
            answer: "Our design team creates stunning environments. We offer floral decor, LED lighting, and customized stage setups."
        },
        {
            keywords: ["photo", "video", "photography", "shoot", "camera"],
            answer: "Capture every moment! We can provide premium photography and videography services as add-ons to your plan."
        },
        {
            keywords: ["music", "dj", "sound", "dance", "entertainment"],
            answer: "Get the party started! We can arrange professional DJs, live bands, and state-of-the-art sound systems."
        },
        {
            keywords: ["support", "help", "contact", "call", "email", "manager"],
            answer: "Need assistance? You can reach our event managers via the Contact page, or call our 24/7 helpline mentioned in the footer."
        },
        {
            keywords: ["customize", "personalize", "change", "add-on"],
            answer: "Absolutely! Every plan is 100% customizable. You can add extra services and adjust guest counts easily on our 'Customize Plan' page."
        },
        {
            keywords: ["venue", "location", "address", "hotel", "place"],
            answer: "We work with top-tier luxury hotels and banquet halls. You can specify your preferred venue while customizing your plan!"
        },
        {
            keywords: ["refund", "cancel", "money back"],
            answer: "Cancellations made 30 days before the event are eligible for a partial refund. Please check our Terms & Conditions for details."
        }
    ];

    let msg = message.toLowerCase();
    let reply = "I'm not quite sure about that. Try asking about weddings, catering, decor, or how to customize your plan!";

    for(let item of knowledge){
        if (item.keywords.some(word => msg.includes(word))) {
            reply = item.answer;
            break;
        }
    }

    // Simulate response delay
    setTimeout(() => {
        botMsg.innerHTML = "<b>Zbot:</b> " + reply;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1200);
}

// add message
function addMessage(sender, text){
    let msg = document.createElement("div");
    msg.className = "chat-msg " + (sender === "You" ? "user-msg" : "bot-msg");
    msg.innerHTML = "<b>"+sender+":</b> "+text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    let msg = document.createElement("div");
    msg.className = "chat-msg bot-msg typing";
    msg.innerHTML = "<b>Zbot:</b> <i>typing...</i>";
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
}


// FAQ buttons
document.querySelectorAll(".faq-btn").forEach(btn=>{
btn.onclick = function(){

userInput.value = this.innerText;
sendMessage();

}
});

});