package ConfigureTopology

var TOPO_MENU string = "/home/arista/menus/%s.yaml"
var BASE_CFGS = []string{"ATD-INFRA"}
var SLEEP_DELAY int = 5

var cp_run_start string = `enable
copy running-config startup-config
`

var cp_start_run string = `enable
copy startup-config running-config
`

// Cmds to grab ZTP status
var ztp_cmds string = `enable
show zerotouch | grep ZeroTouch
`

// Cancel ZTP
var ztp_cancel string = `enable
zerotouch cancel
`
