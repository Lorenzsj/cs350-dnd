var chart = c3.generate({
	bindto:'#DepartmentComparison',
        data: {
            columns: [
                      ['Score', 12000, 9000, 8500, 7500, 3000],
                      ],
            type : 'bar',
            labels: true
        },
        bar: {
            title: "Top Weekly Overall Score:"
	},
        axis: {
	    rotated: true,
            x: {
                label: 'Departments',
		type: 'category',
		categories:['Computer Science','Chemistry','Math', 'Digital Arts', 'Physics']
            },
            y: {
                label: 'Overall Score'
            }
        }

    });


var chart = c3.generate({
	bindto: '#WeeklyOverallChart',
	data: {
	    columns: [
		      ['Score', 1000, 900, 850, 750, 300],
		      ],
	    type : 'bar',
	    labels: true
	},
	bar: {
	    title: "Top Weekly Overall Score:"
	},
	axis: {
	    x: {
		label: 'Username',
		type: 'category',
		categories:['Abigail Matthews', 'Jared Dunbar', 'Sam Roberts', 'Kristina Kolibab', 'Stephen Lorenz']
	    },
	    y: {
		label: 'Overall Score'
	    }
	}
	
    });

var chart = c3.generate({
	bindto:'#WeeklyIndividualChart',
        data: {
            columns: [
                      ['Score', 18, 18, 17, 16, 14],
                      ],
            type : 'bar',
            labels: true
        },
        bar: {
            title: "Top Weekly Indivdual Score:"
	},
        axis: {
            x: {
                label: 'Username',
		type: 'category',
		categories:['Abigail Matthews','Jared Dunbar','Sam Roberts', 'Kristina Koli\
bab', 'Stephen Lorenz']
            },
            y: {
                label: 'Individual Score'
            }
        }

    });

var chart = c3.generate({
	bindto:'#DailyOverallChart',
        data: {
            columns: [
                      ['Score', 1000, 900, 850, 750, 300],
                      ],
            type : 'bar',
            labels: true
        },
        bar: {
            title: "Top Daily Overall Score:"
	},
        axis: {
            x: {
                label: 'Username',
		type: 'category',
		categories:['Abigail Matthews','Jared Dunbar','Sam Roberts', 'Kristina Koli\
bab', 'Stephen Lorenz']
            },
            y: {
                label: 'Overall Score'
            }
        }

    });


var chart = c3.generate({
	bindto:'#DailyIndividualChart',
        data: {
            columns: [
                      ['Score', 15, 13, 12, 12, 10],
                      ],
            type : 'bar',
            labels: true
        },
        bar: {
            title: "Top Daily Individual Score:"
	},
        axis: {
            x: {
                label: 'Username',
		type: 'category',
		categories:['Abigail Matthews','Jared Dunbar','Sam Roberts', 'Kristina Koli\
bab', 'Stephen Lorenz']
            },
            y: {
                label: 'Individual Score'
            }
        }

    });

var chart = c3.generate({
	bindto: '#TopScore',
	data: {
	    columns: [
		      ['Past', 100]
		      ],
	    type : 'donut',
	    onclick: function (d, i) { console.log("onclick", d, i); },
	    onmouseover: function (d, i) { console.log("onmouseover", d, i); },
	    onmouseout: function (d, i) { console.log("onmouseout", d, i); }
	},
	donut: {
	    title: "Total Score"
	}
    });

setTimeout(function () {
	chart.load({
		columns: [
			  ["Daily", 5],
			  ["Weekly", 15]
		]
    });
    }, 1500);