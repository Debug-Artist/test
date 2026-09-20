from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>AgriOptima | Crop Yield Prediction</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <!-- Google Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet">

    <style>
        body {
            font-family: 'Inter', sans-serif;
        }

        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 10px;
        }
    </style>
</head>


<body class="bg-slate-50 text-slate-900">

<div class="min-h-screen">


    <!-- =========================
         SIDEBAR
    ========================== -->

    <aside class="fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-slate-200 hidden lg:flex flex-col">

        <!-- Logo -->

        <div class="px-6 py-6 border-b border-slate-100">

            <div class="flex items-center gap-3">

                <div class="w-11 h-11 rounded-xl bg-emerald-600
                            flex items-center justify-center
                            text-white text-xl shadow-sm">

                    🌱

                </div>

                <div>

                    <h1 class="font-extrabold text-lg tracking-tight">
                        AgriOptima
                    </h1>

                    <p class="text-xs text-slate-400">
                        Yield Intelligence
                    </p>

                </div>

            </div>

        </div>


        <!-- Navigation -->

        <nav class="p-4 space-y-1 text-sm">

            <a href="#dashboard"
               class="flex items-center gap-3 px-3 py-3
                      rounded-xl bg-emerald-50
                      text-emerald-700 font-semibold">

                <span>▦</span>
                Dashboard

            </a>


            <a href="#environment"
               class="flex items-center gap-3 px-3 py-3
                      rounded-xl text-slate-500
                      hover:bg-slate-50">

                <span>☁</span>
                Environment

            </a>


            <a href="#optimization"
               class="flex items-center gap-3 px-3 py-3
                      rounded-xl text-slate-500
                      hover:bg-slate-50">

                <span>∿</span>
                Optimization

            </a>


            <a href="#insights"
               class="flex items-center gap-3 px-3 py-3
                      rounded-xl text-slate-500
                      hover:bg-slate-50">

                <span>◈</span>
                Feature Insights

            </a>

        </nav>


        <!-- Bottom card -->

        <div class="mt-auto p-4">

            <div class="rounded-2xl bg-slate-900
                        text-white p-4">

                <p class="text-xs text-slate-400">
                    Academic Project
                </p>

                <p class="font-semibold mt-1">
                    Crop Yield Predictor
                </p>

                <p class="text-[11px] text-slate-400 mt-2">
                    Mock showcase interface
                </p>

            </div>

        </div>

    </aside>



    <!-- =========================
         MAIN CONTENT
    ========================== -->

    <main class="lg:ml-64">


        <!-- HEADER -->

        <header class="h-20 bg-white/90 backdrop-blur
                       border-b border-slate-200
                       sticky top-0 z-30">

            <div class="h-full px-5 md:px-8
                        flex items-center
                        justify-between">

                <div>

                    <p class="text-xs text-slate-400">
                        Agricultural Intelligence
                    </p>

                    <h2 class="font-bold text-xl">
                        Crop Yield Prediction
                    </h2>

                </div>


                <div class="flex items-center gap-3">

                    <div class="hidden sm:flex items-center gap-2
                                px-3 py-2 rounded-xl
                                bg-slate-50 border border-slate-200
                                text-xs text-slate-500">

                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>

                        Demo Data

                    </div>


                    <button onclick="openChat()"
                            class="px-4 py-2.5 rounded-xl
                                   bg-slate-900 text-white
                                   text-sm font-semibold
                                   hover:bg-slate-800 transition">

                        Ask Agrisense

                    </button>

                </div>

            </div>

        </header>



        <!-- =========================
             DASHBOARD
        ========================== -->

        <div id="dashboard"
             class="p-5 md:p-8 max-w-[1500px] mx-auto">


            <!-- LOCATION -->

            <section class="flex flex-col md:flex-row
                            md:items-end
                            justify-between gap-4 mb-7">

                <div>

                    <div class="inline-flex items-center gap-2
                                text-xs font-semibold
                                text-emerald-700
                                bg-emerald-50
                                border border-emerald-100
                                px-3 py-1.5 rounded-full">

                        ● SAMPLE FARM LOCATION

                    </div>


                    <h3 class="text-3xl md:text-4xl
                               font-extrabold tracking-tight mt-3">

                        Hyderabad, Telangana

                    </h3>


                    <p class="text-sm text-slate-500 mt-1">

                        17.385° N · 78.487° E

                        <span class="mx-1">·</span>

                        Representative agricultural environment

                    </p>

                </div>


                <!-- Crop selector -->

                <select class="bg-white
                               border border-slate-200
                               rounded-xl px-4 py-2.5
                               text-sm outline-none
                               focus:ring-2
                               focus:ring-emerald-200">

                    <option>Rice</option>
                    <option>Maize</option>
                    <option>Chickpea</option>
                    <option>Cotton</option>

                </select>

            </section>



            <!-- =========================
                 KPI CARDS
            ========================== -->

            <section class="grid grid-cols-2
                            xl:grid-cols-4
                            gap-4 mb-5">


                <!-- Temperature -->

                <div class="bg-white
                            border border-slate-200
                            rounded-2xl p-5">

                    <div class="flex justify-between">

                        <span class="text-xs font-semibold
                                     text-slate-400 uppercase">

                            Temperature

                        </span>

                        <span>🌡️</span>

                    </div>


                    <div class="text-3xl font-extrabold mt-3">

                        27.4

                        <span class="text-base font-semibold">
                            °C
                        </span>

                    </div>


                    <p class="text-xs text-slate-400 mt-1">
                        Representative average
                    </p>

                </div>



                <!-- Rainfall -->

                <div class="bg-white
                            border border-slate-200
                            rounded-2xl p-5">

                    <div class="flex justify-between">

                        <span class="text-xs font-semibold
                                     text-slate-400 uppercase">

                            Rainfall

                        </span>

                        <span>🌧️</span>

                    </div>


                    <div class="text-3xl font-extrabold mt-3">

                        842

                        <span class="text-base font-semibold">
                            mm
                        </span>

                    </div>


                    <p class="text-xs text-slate-400 mt-1">
                        Seasonal sample value
                    </p>

                </div>



                <!-- Soil pH -->

                <div class="bg-white
                            border border-slate-200
                            rounded-2xl p-5">

                    <div class="flex justify-between">

                        <span class="text-xs font-semibold
                                     text-slate-400 uppercase">

                            Soil pH

                        </span>

                        <span>🧪</span>

                    </div>


                    <div class="text-3xl font-extrabold mt-3">
                        6.7
                    </div>


                    <p class="text-xs text-emerald-600
                              mt-1 font-semibold">

                        Near neutral range

                    </p>

                </div>



                <!-- Predicted Yield -->

                <div class="bg-white
                            border border-slate-200
                            rounded-2xl p-5">

                    <div class="flex justify-between">

                        <span class="text-xs font-semibold
                                     text-slate-400 uppercase">

                            Predicted Yield

                        </span>

                        <span>🌾</span>

                    </div>


                    <div class="text-3xl font-extrabold mt-3">

                        3.84

                        <span class="text-base font-semibold">
                            t/ha
                        </span>

                    </div>


                    <p class="text-xs text-slate-400 mt-1">
                        Illustrative model output
                    </p>

                </div>

            </section>



            <!-- =========================
                 ENVIRONMENT SECTION
            ========================== -->

            <section id="environment"
                     class="grid xl:grid-cols-3
                            gap-5">


                <!-- Weather Chart -->

                <div class="xl:col-span-2
                            bg-white
                            border border-slate-200
                            rounded-2xl p-5 md:p-6">

                    <div class="flex flex-col sm:flex-row
                                sm:items-center
                                justify-between gap-3 mb-5">

                        <div>

                            <h3 class="font-bold text-lg">
                                Weather Profile
                            </h3>

                            <p class="text-xs text-slate-400 mt-1">
                                Representative temperature
                                and rainfall pattern
                            </p>

                        </div>


                        <span class="text-xs
                                     bg-slate-50
                                     px-3 py-2
                                     rounded-lg
                                     text-slate-500">

                            Monsoon Season · Sample

                        </span>

                    </div>


                    <div class="h-72">

                        <canvas id="weatherChart"></canvas>

                    </div>

                </div>



                <!-- Soil -->

                <div class="bg-white
                            border border-slate-200
                            rounded-2xl p-5 md:p-6">

                    <div class="flex justify-between">

                        <div>

                            <h3 class="font-bold text-lg">
                                Soil Profile
                            </h3>

                            <p class="text-xs text-slate-400 mt-1">
                                Sample soil measurements
                            </p>

                        </div>


                        <span class="text-xs
                                     bg-amber-50
                                     text-amber-700
                                     px-2.5 py-1
                                     rounded-lg">

                            Loamy

                        </span>

                    </div>



                    <div class="space-y-5 mt-7">


                        <!-- Nitrogen -->

                        <div>

                            <div class="flex justify-between
                                        text-sm mb-2">

                                <span>Nitrogen</span>

                                <b>68 kg/ha</b>

                            </div>


                            <div class="h-2 bg-slate-100
                                        rounded-full overflow-hidden">

                                <div class="h-full
                                            bg-emerald-500
                                            rounded-full"
                                     style="width:68%">
                                </div>

                            </div>

                        </div>



                        <!-- Phosphorus -->

                        <div>

                            <div class="flex justify-between
                                        text-sm mb-2">

                                <span>Phosphorus</span>

                                <b>42 kg/ha</b>

                            </div>


                            <div class="h-2 bg-slate-100
                                        rounded-full overflow-hidden">

                                <div class="h-full
                                            bg-emerald-500
                                            rounded-full"
                                     style="width:52%">
                                </div>

                            </div>

                        </div>



                        <!-- Potassium -->

                        <div>

                            <div class="flex justify-between
                                        text-sm mb-2">

                                <span>Potassium</span>

                                <b>51 kg/ha</b>

                            </div>


                            <div class="h-2 bg-slate-100
                                        rounded-full overflow-hidden">

                                <div class="h-full
                                            bg-emerald-500
                                            rounded-full"
                                     style="width:59%">
                                </div>

                            </div>

                        </div>



                        <!-- Moisture -->

                        <div>

                            <div class="flex justify-between
                                        text-sm mb-2">

                                <span>Soil Moisture</span>

                                <b>61%</b>

                            </div>


                            <div class="h-2 bg-slate-100
                                        rounded-full overflow-hidden">

                                <div class="h-full
                                            bg-blue-500
                                            rounded-full"
                                     style="width:61%">
                                </div>

                            </div>

                        </div>

                    </div>



                    <div class="mt-7 pt-5
                                border-t border-slate-100
                                flex justify-between">

                        <span class="text-sm text-slate-500">
                            Soil pH
                        </span>

                        <span class="font-bold">
                            6.7
                        </span>

                    </div>

                </div>

            </section>



            <!-- =========================
                 OPTIMIZATION + INSIGHTS
            ========================== -->

            <section class="grid xl:grid-cols-2
                            gap-5 mt-5">


                <!-- Optimization -->

                <div id="optimization"
                     class="bg-white
                            border border-slate-200
                            rounded-2xl p-5 md:p-6">

                    <h3 class="font-bold text-lg">
                        Optimization Comparison
                    </h3>

                    <p class="text-xs text-slate-400 mt-1">
                        Illustrative convergence behaviour
                    </p>


                    <div class="h-64 mt-5">

                        <canvas id="optimizerChart"></canvas>

                    </div>

                </div>



                <!-- Partial Derivatives -->

                <div id="insights"
                     class="bg-white
                            border border-slate-200
                            rounded-2xl p-5 md:p-6">

                    <h3 class="font-bold text-lg">
                        Partial-Derivative Insights
                    </h3>

                    <p class="text-xs text-slate-400 mt-1">
                        Feature sensitivity in the regression model
                    </p>



                    <div class="space-y-3 mt-5">


                        <!-- Rainfall -->

                        <div class="flex items-center
                                    justify-between
                                    p-4 rounded-xl
                                    bg-slate-50">

                            <div>

                                <p class="font-semibold text-sm">
                                    ∂Yield / ∂Rainfall
                                </p>

                                <p class="text-xs text-slate-400">
                                    Sensitivity estimate
                                </p>

                            </div>


                            <span class="font-bold
                                         text-emerald-600">

                                +0.018

                            </span>

                        </div>



                        <!-- Temperature -->

                        <div class="flex items-center
                                    justify-between
                                    p-4 rounded-xl
                                    bg-slate-50">

                            <div>

                                <p class="font-semibold text-sm">
                                    ∂Yield / ∂Temperature
                                </p>

                                <p class="text-xs text-slate-400">
                                    Sensitivity estimate
                                </p>

                            </div>


                            <span class="font-bold
                                         text-emerald-600">

                                +0.074

                            </span>

                        </div>



                        <!-- pH -->

                        <div class="flex items-center
                                    justify-between
                                    p-4 rounded-xl
                                    bg-slate-50">

                            <div>

                                <p class="font-semibold text-sm">
                                    ∂Yield / ∂Soil pH
                                </p>

                                <p class="text-xs text-slate-400">
                                    Sensitivity estimate
                                </p>

                            </div>


                            <span class="font-bold text-rose-500">

                                −0.031

                            </span>

                        </div>

                    </div>



                    <div class="mt-5 p-4 rounded-xl
                                border border-dashed
                                border-slate-200
                                text-xs text-slate-500
                                leading-5">

                        <b class="text-slate-700">
                            Interpretation:
                        </b>

                        These are mock sensitivity values
                        for the presentation interface.
                        The final application can calculate
                        them directly from the trained
                        regression model.

                    </div>

                </div>

            </section>



            <!-- =========================
                 PIPELINE
            ========================== -->

            <section class="mt-5
                            bg-slate-900
                            text-white
                            rounded-2xl
                            p-5 md:p-6
                            flex flex-col
                            md:flex-row
                            md:items-center
                            justify-between gap-4">

                <div>

                    <p class="text-xs
                              text-slate-400
                              uppercase
                              tracking-wider">

                        Model Pipeline

                    </p>


                    <p class="font-semibold mt-1">

                        Regression

                        <span class="text-slate-500 mx-1">→</span>

                        Gradient Descent

                        <span class="text-slate-500 mx-1">→</span>

                        Momentum

                        <span class="text-slate-500 mx-1">→</span>

                        Adam

                        <span class="text-slate-500 mx-1">→</span>

                        Feature Sensitivity

                    </p>

                </div>


                <span class="text-xs
                             px-3 py-2
                             rounded-lg
                             bg-white/10">

                    SHOWCASE MODE

                </span>

            </section>



            <!-- Footer -->

            <footer class="py-8
                           text-center
                           text-xs
                           text-slate-400">

                AgriOptima · Crop Yield Prediction
                Academic Project

            </footer>

        </div>

    </main>

</div>



<!-- ===================================================
     CHAT OVERLAY
==================================================== -->

<div id="chatOverlay"
     class="fixed inset-0
            bg-slate-950/30
            backdrop-blur-sm
            hidden z-40"
     onclick="closeChat()">
</div>



<!-- ===================================================
     CHAT PANEL
==================================================== -->

<div id="chatPanel"
     class="fixed right-0 top-0 bottom-0
            w-full sm:w-[420px]
            bg-white shadow-2xl
            translate-x-full
            transition-transform
            duration-300
            z-50
            flex flex-col">


    <!-- Chat Header -->

    <div class="px-5 py-4
                border-b border-slate-200
                flex items-center
                justify-between">

        <div>

            <p class="font-bold">
                Agrisense
            </p>

            <p class="text-xs text-slate-400">
                Crop Yield Assistant · Demo
            </p>

        </div>


        <button onclick="closeChat()"
                class="w-9 h-9
                       rounded-lg
                       hover:bg-slate-100">

            ✕

        </button>

    </div>



    <!-- Messages -->

    <div id="chatMessages"
         class="flex-1
                overflow-y-auto
                p-5 space-y-4">


        <div class="bg-slate-100
                    rounded-2xl
                    rounded-tl-sm
                    p-4
                    text-sm
                    leading-6
                    max-w-[90%]">

            Hello! I'm the Agrisense
            demo assistant.

            <br><br>

            You can ask about:

            <br>
            • rainfall
            <br>
            • temperature
            <br>
            • soil pH
            <br>
            • crop yield
            <br>
            • Gradient Descent
            <br>
            • Momentum
            <br>
            • Adam

            <br><br>

            <span class="text-slate-400 text-xs">
                AI responses are disabled in this mock showcase.
            </span>

        </div>

    </div>



    <!-- Chat Input -->

    <div class="border-t
                border-slate-200
                p-4">

        <div class="flex gap-2">

            <input id="chatInput"
                   class="flex-1
                          border border-slate-200
                          rounded-xl
                          px-4 py-3
                          text-sm
                          outline-none
                          focus:ring-2
                          focus:ring-emerald-200"
                   placeholder="Ask about this farm...">


            <button onclick="sendDemoMessage()"
                    class="px-4
                           rounded-xl
                           bg-slate-900
                           text-white
                           text-sm
                           font-semibold">

                Send

            </button>

        </div>


        <p class="text-[10px]
                  text-slate-400
                  mt-2">

            Demo interface — AI functionality is
            intentionally disabled.

        </p>

    </div>

</div>



<!-- ===================================================
     JAVASCRIPT
==================================================== -->

<script>


/* ==========================================
   WEATHER CHART
========================================== */

const weatherCanvas =
    document.getElementById("weatherChart");


new Chart(weatherCanvas, {

    type: "line",

    data: {

        labels: [
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov"
        ],

        datasets: [

            {

                label: "Temperature °C",

                data: [
                    29.1,
                    27.8,
                    27.2,
                    27.4,
                    26.8,
                    25.4
                ],

                borderWidth: 2,

                tension: 0.35,

                yAxisID: "temperature"

            },


            {

                label: "Rainfall mm",

                data: [
                    112,
                    168,
                    142,
                    119,
                    74,
                    24
                ],

                borderWidth: 2,

                tension: 0.35,

                yAxisID: "rainfall"

            }

        ]

    },


    options: {

        responsive: true,

        maintainAspectRatio: false,

        interaction: {

            mode: "index",

            intersect: false

        },

        plugins: {

            legend: {

                labels: {

                    usePointStyle: true,

                    boxWidth: 8

                }

            }

        },


        scales: {

            temperature: {

                position: "left",

                grid: {

                    color: "#f1f5f9"

                }

            },


            rainfall: {

                position: "right",

                grid: {

                    drawOnChartArea: false

                }

            },


            x: {

                grid: {

                    display: false

                }

            }

        }

    }

});



/* ==========================================
   OPTIMIZER CHART
========================================== */

const optimizerCanvas =
    document.getElementById("optimizerChart");


new Chart(optimizerCanvas, {

    type: "line",

    data: {

        labels: [
            "0",
            "10",
            "20",
            "30",
            "40",
            "50",
            "60",
            "70",
            "80",
            "90",
            "100"
        ],

        datasets: [

            {

                label: "Vanilla GD",

                data: [
                    1.00,
                    0.82,
                    0.68,
                    0.57,
                    0.49,
                    0.43,
                    0.39,
                    0.35,
                    0.32,
                    0.30,
                    0.29
                ],

                borderWidth: 2,

                tension: 0.35

            },


            {

                label: "Momentum",

                data: [
                    1.00,
                    0.66,
                    0.43,
                    0.30,
                    0.22,
                    0.17,
                    0.14,
                    0.12,
                    0.11,
                    0.105,
                    0.10
                ],

                borderWidth: 2,

                tension: 0.35

            },


            {

                label: "Adam",

                data: [
                    1.00,
                    0.48,
                    0.26,
                    0.16,
                    0.115,
                    0.09,
                    0.075,
                    0.067,
                    0.062,
                    0.059,
                    0.057
                ],

                borderWidth: 2,

                tension: 0.35

            }

        ]

    },


    options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

            legend: {

                labels: {

                    usePointStyle: true,

                    boxWidth: 8

                }

            }

        },


        scales: {

            y: {

                title: {

                    display: true,

                    text: "Loss"

                },

                grid: {

                    color: "#f1f5f9"

                }

            },


            x: {

                title: {

                    display: true,

                    text: "Iterations"

                },

                grid: {

                    display: false

                }

            }

        }

    }

});



/* ==========================================
   OPEN CHAT
========================================== */

function openChat() {

    document
        .getElementById("chatPanel")
        .classList
        .remove("translate-x-full");


    document
        .getElementById("chatOverlay")
        .classList
        .remove("hidden");

}



/* ==========================================
   CLOSE CHAT
========================================== */

function closeChat() {

    document
        .getElementById("chatPanel")
        .classList
        .add("translate-x-full");


    document
        .getElementById("chatOverlay")
        .classList
        .add("hidden");

}



/* ==========================================
   DEMO CHAT
========================================== */

function sendDemoMessage() {

    const input =
        document.getElementById("chatInput");

    const messages =
        document.getElementById("chatMessages");


    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    /* User message */

    const userMessage =
        document.createElement("div");


    userMessage.className =
        "ml-auto bg-slate-900 text-white " +
        "rounded-2xl rounded-tr-sm p-4 " +
        "text-sm leading-6 max-w-[90%]";


    userMessage.textContent =
        message;


    messages.appendChild(userMessage);


    input.value = "";


    messages.scrollTop =
        messages.scrollHeight;



    /* Fake showcase response */

    setTimeout(function() {

        const botMessage =
            document.createElement("div");


        botMessage.className =
            "bg-slate-100 rounded-2xl " +
            "rounded-tl-sm p-4 text-sm " +
            "leading-6 max-w-[90%]";


        botMessage.textContent =
            "This is a mock dashboard. " +
            "The AI prediction and chat engine " +
            "will be connected in the final version.";


        messages.appendChild(botMessage);


        messages.scrollTop =
            messages.scrollHeight;

    }, 400);

}



/* ==========================================
   ENTER KEY FOR CHAT
========================================== */

document
    .getElementById("chatInput")
    .addEventListener("keydown", function(event) {

        if (event.key === "Enter") {

            sendDemoMessage();

        }

    });


</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/health")
def health():
    return {
        "status": "ok",
        "project": "Crop Yield Prediction Dashboard"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )
