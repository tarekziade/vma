var dataVMASpeed;
var dataFractionne = [];

var VMASpeedDatatable = jQuery('#VMASpeed').DataTable({
  paging: false,
  searching: false,
  ordering: false,
  info: false,
  responsive: true,
  data: dataVMASpeed,
  columns: [
    { data: 'vma' },
    { data: '60%' },
    { data: '65%' },
    { data: '70%' },
    { data: '75%' },
    { data: '80%' },
    { data: '85%' },
    { data: '90%' },
    { data: '95%' },
    { data: '100%' },
    { data: '105%' },
    { data: '110%' },
    { data: '115%' }
  ]
})

var FractionneDatatable = jQuery('#Fractionne').DataTable({
  responsive: true,
  paging: false,
  searching: false,
  ordering: false,
  info: false,
  data: dataFractionne,
  columns: [
    { data: 'vma' },
    { data: '65%' },
    { data: '70%' },
    { data: '75%' },
    { data: '80%' },
    { data: '85%' },
    { data: '90%' },
    { data: '95%' },
    { data: '100%' },
    { data: '105%' },
    { data: '110%' },
    { data: '115%' }
  ]
})

function calculateVMA (time) {
  var result = ''
  time = (Math.round(time * 10)) / 10

  var min = (time - (time % 60)) / 60
  if (min > 0) { result = result + pad(min) + 'm' }

  var sec = (Math.round((time % 60) * 10)) / 10
  if (sec > 0) { result = result + pad(Math.round(sec)) + 's' }

  var hour = Math.floor(min / 60) + 'h' + '' + pad(min % 60)
  if (min > 60) { result = hour + 'm' }

  if (result.substr(0, 1) === '0') { result = result.substr(1) }

  return result.trim()
}

function indexToType (i) {
  if (i <= 65) return "<span title='Récupération'>R</span>"
  if (i <= 75) return "<span title='Endurance fondamentale'>EF</span>"
  if (i <= 80) return "<span title='Marathon'>M</span>"
  if (i <= 85) return "<span title='Semi-marathon'>Semi</span>"
  if (i <= 90) return "<span title='10 Kilomètres'>10K</span>"
  if (i < 95) return "<span title='5 Kilomètres'>5K</span>"
  if (i <= 100) return "<span title='Fractionné Extensif'>FE</span>"
  if (i <= 110) return "<span title='Fractionné Intensif'>FI</span>"
  return 'Sprint'
}

function calculateVMASpeedData (mas, min, max, interval) {
  // first label
  dataVMASpeed = [{ vma: 'Vitesse' }, { vma: 'Allure' },
    { vma: 'Type' }]
  var label = ''

  // calculate data
  for (var i = min; i <= max; i += interval) {
    // construct the key to match the input name
    label = i.toString() + '%'
    // append data on speed object
    var speed = Math.round(mas * i) / 100
    var vma = calculateVMA(3600 / speed)
    dataVMASpeed[0][label] = speed
    dataVMASpeed[1][label] = vma
    dataVMASpeed[2][label] = indexToType(i)
  }
};

function calculateFractionne (total, min, max, interval, distance, customLabel) {
  let dataFractionneLine
  if (customLabel != null) {
    dataFractionneLine = { vma: customLabel }
  } else {
    dataFractionneLine = { vma: distance + ' m' }
  }
  for (let i = min; i <= max; i += interval) {
    const label = i.toString() + '%'
    dataFractionneLine[label] = calculateVMA(total / i * distance)
  }
  dataFractionne.push(dataFractionneLine)
};

function init (mas) {
  const MAS = mas
  const masMs = MAS * 1000 / 3600
  const total = 100 / masMs

  calculateVMASpeedData(MAS, 60, 115, 5)

  // distance de 100 a 1000
  for (let distance = 100; distance < 1000; distance += 100) {
    if (distance === 700 || distance === 900) continue
    calculateFractionne(total, 65, 115, 5, distance)
  }
  // 1000 a 5000
  for (let distance = 1000; distance <= 5000; distance += 1000) {
    calculateFractionne(total, 65, 115, 5, distance)
  }

  // 10 km
  calculateFractionne(total, 65, 115, 5, 10000, '10 km')
  // semi
  calculateFractionne(total, 65, 115, 5, 21100, 'Semi')
  // marathon
  calculateFractionne(total, 65, 115, 5, 42200, 'Marathon')
  // 100 km
  calculateFractionne(total, 65, 115, 5, 100000, '100 km')
}

function pad (num) {
  var s = '' + num
  if (s.length < 2) return '0' + s
  return s
}

function validate () {
  var speed = getCookie('vma')
  VMASpeedDatatable.clear().draw()
  FractionneDatatable.clear().draw()
  init(speed)
  VMASpeedDatatable.rows.add(dataVMASpeed).draw()
  FractionneDatatable.rows.add(dataFractionne).draw()

  // let's find out the speed of short intervals (95/100)
  //
  // 100M -
  FractionneDatatable.cells(0, 8).nodes()[0].style.cssText = 'background-color: #FF6961'
  FractionneDatatable.cells(0, 9).nodes()[0].style.cssText = 'background-color: #FF6961'

  // 200M -
  FractionneDatatable.cells(1, 8).nodes()[0].style.cssText = 'background-color: #FF6961'
  FractionneDatatable.cells(1, 9).nodes()[0].style.cssText = 'background-color: #FF6961'

  // 300M -
  FractionneDatatable.cells(2, 7).nodes()[0].style.cssText = 'background-color: #FF6961'
  FractionneDatatable.cells(2, 8).nodes()[0].style.cssText = 'background-color: #FF6961'
  FractionneDatatable.cells(2, 9).nodes()[0].style.cssText = 'background-color: #FF6961'

  // 400M -
  FractionneDatatable.cells(3, 7).nodes()[0].style.cssText = 'background-color: #FF8361'
  FractionneDatatable.cells(3, 8).nodes()[0].style.cssText = 'background-color: #FF8361'

  // 500M -
  FractionneDatatable.cells(4, 7).nodes()[0].style.cssText = 'background-color: #FF8361'
  FractionneDatatable.cells(4, 8).nodes()[0].style.cssText = 'background-color: #FF8361'

  // 600M -
  FractionneDatatable.cells(5, 6).nodes()[0].style.cssText = 'background-color: #FF8361'
  FractionneDatatable.cells(5, 7).nodes()[0].style.cssText = 'background-color: #FF8361'
  FractionneDatatable.cells(5, 8).nodes()[0].style.cssText = 'background-color: #FF8361'

  // 800M -
  FractionneDatatable.cells(6, 6).nodes()[0].style.cssText = 'background-color: #FF9E61'
  FractionneDatatable.cells(6, 7).nodes()[0].style.cssText = 'background-color: #FF9E61'

  // 1000M -
  FractionneDatatable.cells(7, 6).nodes()[0].style.cssText = 'background-color: #FF9E61'
  FractionneDatatable.cells(7, 7).nodes()[0].style.cssText = 'background-color: #FF9E61'

  // 5000M -
  FractionneDatatable.cells(11, 6).nodes()[0].style.cssText = 'background-color: #87FF8D'
  FractionneDatatable.cells(11, 7).nodes()[0].style.cssText = 'background-color: #87FF8D'

  // 10 -
  FractionneDatatable.cells(12, 5).nodes()[0].style.cssText = 'background-color: #87FF8D'
  FractionneDatatable.cells(12, 6).nodes()[0].style.cssText = 'background-color: #87FF8D'

  // semi -
  FractionneDatatable.cells(13, 4).nodes()[0].style.cssText = 'background-color: #87FF8D'
  FractionneDatatable.cells(13, 5).nodes()[0].style.cssText = 'background-color: #87FF8D'

  // marathon -
  FractionneDatatable.cells(14, 2).nodes()[0].style.cssText = 'background-color: #87FF8D'
  FractionneDatatable.cells(14, 3).nodes()[0].style.cssText = 'background-color: #87FF8D'
  FractionneDatatable.cells(14, 4).nodes()[0].style.cssText = 'background-color: #87FF8D'

  // 100 -
  FractionneDatatable.cells(15, 1).nodes()[0].style.cssText = 'background-color: #87FF8D'
}

validate()
