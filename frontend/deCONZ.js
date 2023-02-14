define([
    'app'
],

function(app) {

    var renameDeviceModal = {
        templateUrl: 'app/deCONZ/RenameModal.html',
        controllerAs: '$ctrl',
        controller: function($scope, $rootScope, apiDeCONZ) {
            var $ctrl = this;

            $ctrl.isUnchanged = true;
            $ctrl.device = Object.assign($scope.device);
            $ctrl.myname = $ctrl.device.name
            $ctrl.renameDevice = function() {

                $ctrl.isSaving = true;

                // Make api call here
                payload = new Object()
                payload.name = $ctrl.myname
                JSONpayload = angular.toJson(payload)

                // console.log('Renaming -> ' + 'deviceclass: ' + $ctrl.device.deviceclass + '\nDevice ID: ' + $ctrl.device.id + '\nBody: ' + JSONpayload);

                apiDeCONZ.setDeCONZdata($ctrl.device.deviceclass, 'PUT', $ctrl.device.id, JSONpayload,'')
                .then(function() {
                    // console.log('Device name updated')
                    $scope.$emit("refreshDeCONZfunc", $ctrl.device.deviceclass);
                })
                .then($scope.$close())
            }
        }
    };

    var includeDeviceModal = {
        templateUrl: 'app/deCONZ/IncludeModal.html',
        controllerAs: '$ctrl',
        controller: function($scope, $rootScope, apiDeCONZ) {
            var $ctrl = this;

            $ctrl.isUnchanged = true;
            $ctrl.device = Object.assign($scope.device);
            $ctrl.myname = "XX:XX:XX:XX:XX:XX:XX:XX-XX-XXXX"
            $ctrl.includeDevice = function() {

                $ctrl.isSaving = true;

                // Make api call here
                payload = new Object()
                JSONpayload = angular.toJson(payload)

                // console.log('Renaming -> ' + 'deviceclass: ' + $ctrl.device.deviceclass + '\nDevice ID: ' + $ctrl.device.id + '\nBody: ' + JSONpayload);

                apiDeCONZ.setDeCONZdata($ctrl.device.deviceclass, 'PUT', '1', JSONpayload,'device/' + $ctrl.myname)
                .then(function() {
                    // console.log('Device name updated')
                    $scope.$emit("refreshDeCONZfunc", $ctrl.device.deviceclass);
                })
                .then($scope.$close())
            }
        }
    };

    var includeremDeviceModal = {
        templateUrl: 'app/deCONZ/IncluderemModal.html',
        controllerAs: '$ctrl',
        controller: function($scope, $rootScope, apiDeCONZ) {
            var $ctrl = this;

            $ctrl.isUnchanged = true;
            $ctrl.device = Object.assign($scope.device);
            $ctrl.myname = "XX:XX:XX:XX:XX:XX:XX:XX-XX-XXXX"
            $ctrl.includeremDevice = function() {

                $ctrl.isSaving = true;

                // Make api call here
                payload = new Object()
                payload.name = $ctrl.myname
                JSONpayload = angular.toJson(payload)

                // console.log('Renaming -> ' + 'deviceclass: ' + $ctrl.device.deviceclass + '\nDevice ID: ' + $ctrl.device.id + '\nBody: ' + JSONpayload);

                apiDeCONZ.setDeCONZdata($ctrl.device.deviceclass, 'DELETE', $ctrl.device.id, JSONpayload,'')
                .then(function() {
                    // console.log('Device name updated')
                    $scope.$emit("refreshDeCONZfunc", $ctrl.device.deviceclass);
                })
                .then($scope.$close())
            }
        }
    };

    var configDeviceModal = {
        templateUrl: 'app/deCONZ/ConfigModal.html',
        controllerAs: '$ctrl',
        controller: function($scope, $rootScope, apiDeCONZ) {
            var $ctrl = this;

            $ctrl.isUnchanged = true;
            $ctrl.device = Object.assign($scope.device);
            $ctrl.myname = $ctrl.device.name
            $ctrl.deviceconfig = $ctrl.device.config
            let oldconfig = Object.assign({}, $ctrl.device.config);
            $ctrl.configDevice = function() {

                $ctrl.isSaving = true;

                // Make api call here
                payload = new Object()

                for (const [key, value] of Object.entries($ctrl.deviceconfig)) {
                  if ( oldconfig[key] != value ) {
                      newvalue = value
                      if (!isNaN(newvalue))
                      {
                        newvalue = parseInt(newvalue);
                      }
                      if(value[0] == "'") { newvalue = value.slice(1, -1);}
                      if (newvalue == 'false') { newvalue = false; }
                      if (newvalue == 'true') { newvalue = true; }
                      payload[key] = newvalue;
                  }
                }

                //payload.name = $ctrl.myname
                JSONpayload = angular.toJson(payload)

                console.log('Config -> ' + 'deviceclass: ' + $ctrl.device.deviceclass + '\nDevice ID: ' + $ctrl.device.id + '\nBody: ' + JSONpayload);

                apiDeCONZ.setDeCONZdata($ctrl.device.deviceclass, 'PUT', $ctrl.device.id, JSONpayload,'config')
                .then(function() {
                //    console.log('Device setting updated')
                    $scope.$emit("refreshDeCONZfunc", $ctrl.device.deviceclass);
                })
                .then($scope.$close())

            }
        }
    };

    var deleteDeviceModal = {
        templateUrl: 'app/deCONZ/DeleteModal.html',
        controllerAs: '$ctrl',
        controller: function($scope, $rootScope, apiDeCONZ) {
            var $ctrl = this;

            $ctrl.device = Object.assign($scope.device);
            $ctrl.myname = $ctrl.device.name
            $ctrl.deleteDevice = function() {

                // Make api call here
                // console.log('Deleting -> ' + 'deviceclass: ' + $ctrl.device.deviceclass + '\nDevice ID: ' + $ctrl.device.id );

                apiDeCONZ.setDeCONZdata($ctrl.device.deviceclass, 'DELETE', $ctrl.device.id,'')
                .then(function() {
                    // console.log('Device deleted')
                    $scope.$emit("refreshDeCONZfunc", $ctrl.device.deviceclass);
                })
                .then($scope.$close())

                $scope.$close()
            }
        }
    };

    app.component('zzDeconzPlugin', {
        templateUrl: 'app/deCONZ/index.html',
        controller: deCONZController,
    })

    app.component('zzDeconzPluginsTable', {
        bindings: {
            zigdevs: '<',
            onSelect: '&',
            onUpdate: '&'
        },
        template: '<table id="zz-deconz-plugins" class="display" width="100%"></table>',
        controller: zzDeconzPluginsTableController,
    });

    function deCONZController($uibModal, $scope, $location, apiDeCONZ) {

        var $ctrl = this
        $ctrl.refreshDeCONZ = refreshDeCONZ;
        $ctrl.permitJoins = permitJoins;
        $ctrl.autoConfPlugin = autoConfPlugin;

        $ctrl.$onInit = function() {
            refreshDeCONZ('lights');
        }

        $scope.$on("refreshDeCONZfunc", function (evt, data) {
            refreshDeCONZ(data);
        });

        function refreshDeCONZ(deviceClass) {
            apiDeCONZ.getDeCONZdata(deviceClass).then(function(zigdevs) {
                // console.log('Returned Data Zigbee Devices')
                $ctrl.zigdevs = Object.values(zigdevs)
                $ctrl.value = deviceClass

            })
        }

        function permitJoins(seconds = 60) {
            var JSONpayload

            $ctrl.isJoining = true;

            payload = new Object()
            payload.permitjoin = seconds
            JSONpayload = angular.toJson(payload)

            apiDeCONZ.setDeCONZdata('config', 'PUT', '', JSONpayload,'').then(function() {
                // console.log('Permit Join activated')
            })
            .then($uibModal.open({
                templateUrl: 'app/deCONZ/PermitJoinsModal.html',
                controllerAs: '$mctrl',
                controller: function($scope, $interval, apiDeCONZ) {
                    var $mctrl = this;

                        $scope.countdown = seconds;

                    var timer = $interval(function () {
                        if ($scope.countdown > 0){
                            $scope.countdown--;
                        } else {
                            $ctrl.isJoining = false;
                            $interval.cancel(timer);
                            // console.log('Countdown end')
                            apiDeCONZ.getDeCONZdata($ctrl.value).then(function(zigdevs) {
                                // console.log('Returned Zigbee device data')
                                $ctrl.zigdevs = Object.values(zigdevs)
                            });
                            $scope.$close();
                        }
                    }, 1000);

                    $mctrl.endPermit = function() {

                        // console.log('End Permit')

                        payload = new Object()
                        payload.permitjoin = 0
                        JSONpayload = angular.toJson(payload)

                        apiDeCONZ.setDeCONZdata('config', 'PUT', '', JSONpayload,'').then(function() {
                            // console.log('Permit Join de-activated')
                        })
                        .then(apiDeCONZ.getDeCONZdata($ctrl.value).then(function(zigdevs) {
                            // console.log('Returned Zigbee device data')
                            $ctrl.zigdevs = Object.values(zigdevs)
                        }))

                        $ctrl.isJoining = false;

                        $scope.$close();
                    }
                }
            })
            );
        }

        function autoConfPlugin() {
            let configOutput

            apiDeCONZ.checkDeCONZsetup()
            .then(configOutput => $uibModal.open({
                templateUrl: 'app/deCONZ/autoConfPluginModal.html',
                controllerAs: '$mctrl',
                controller: function($scope, $interval, apiDeCONZ) {
                    var $mctrl = this;

                    $scope.apiShowGet = true

                    $scope.apiCancelButton = $.t('Cancel')

                    $scope.configOutput = angular.fromJson(configOutput)

                    $mctrl.getAPIkey = function() {

                        payload = new Object()
                        payload.devicetype = "domoticz_deconz"
                        JSONpayload = angular.toJson(payload)

                        apiDeCONZ.postDeCONZdata(configOutput[0].internalipaddress, configOutput[0].internalport, 'api', JSONpayload, $mctrl.gwPassword).then(function(response) {
                            // console.log('Response was: ' + angular.toJson(response, true))
                            if ("success" in response[0]) {
                                response[0].API_KEY = response[0].success.username
                                delete response[0].success;
                                $scope.apiShowGet = false
                                $scope.apiCancelButton = $.t('Close')
                            }

                            $scope.configOutput1 = response
                        })
                    }

                    $mctrl.setcode0 = function() {

                        payload = new Object()
                        payload.code0 = $mctrl.gwPassword
                        JSONpayload = angular.toJson(payload)
                        apiDeCONZ.setDeCONZdata('alarmsystems', 'PUT', "1", JSONpayload,'config').then(function(response) {
                            // console.log('Response was: ' + angular.toJson(response, true))
                            if ("success" in response[0]) {
                                response[0].Response = "Code 0 Updated"
                                delete response[0].success;
                                $scope.apiShowGet = false
                                $scope.apiCancelButton = $.t('Close')
                            }

                            $scope.configOutput1 = response
                        })
                    }

                    $mctrl.cleanAPIkey = function() {

                        payload = new Object()
                        payload.devicetype = "domoticz_deconz"
                        key_list = {}

                        apiDeCONZ.getDeCONZdata("config").then(function(response) {
                            // console.log('Returned Data Zigbee Devices')
                            key_list = angular.toJson(response, true)
                            key_list = response["whitelist"]


                            for(var k in key_list) {
                                 if ((key_list[k]["name"].indexOf("Phoscon#") != -1) ||
                                     (key_list[k]["name"].indexOf("deCONZ WebApp") != -1) ||
                                     (key_list[k]["name"].indexOf("Hue Essentials#") != -1) ||
                                     (key_list[k]["name"].indexOf("homebridge-hue#") != -1))
                                 {
                                    apiDeCONZ.setDeCONZdata('config/whitelist/' + k, 'DELETE', '', '','').then(function() {
                                        //console.log('Delete API Key : ' + k )
                                    })
                                 }
                            }

                        })

                    }

                    $mctrl.ConfPlugin = function() {

                        payload = new Object()
                        payload.devicetype = "domoticz_deconz"
                        //JSONpayload = angular.toJson(payload)

                        apiDeCONZ.getDeCONZdata("config").then(function(response) {
                            // console.log('Returned Data Zigbee Devices')
                            bootbox.alert('<pre>' + angular.toJson(response, true) + '</pre>')
                        })
                    }
                }
            })
            );
        }

    }

    app.factory('apiDeCONZ', function($http, $location, $q, $compile, $rootScope, domoticzApi) {
        var requestsCount = 0;
        var requestsQueue = [];
        var apiHost = "";
        var apiPort = "";
        var apiKey = "";
        var onInit = init();

        return {
            sendRequest: sendRequest,
            checkDeCONZsetup: checkDeCONZsetup,
            getDeCONZdata: getDeCONZdata,
            setDeCONZdata: setDeCONZdata,
            postDeCONZdata: postDeCONZdata,
        };

        function init() {

            return domoticzApi.sendRequest({
                type: 'hardware',
                displayhidden: 1,
                filter: 'all',
                used: 'all'
            })
                .then(domoticzApi.errorHandler)
                .then(function(response) {
                    if (response.result === undefined) {
                        throw new Error('No Plugin devices found')
                    }

                    var apiDevice = response.result
                            .find(function(plugin) {
                            return plugin.Extra === 'deCONZ'
                        })

                    if (!apiDevice) {
                        throw new Error('No API Device found')
                    }
                    // console.log('Setting API data: ' + apiDevice.Address + '\n' + apiDevice.Port + '\n' + apiDevice.Mode2)

                    if (apiDevice.Address == '127.0.0.1' | apiDevice.Address == 'localhost') {
                        // console.log('host is: ' + $location.host())
                        apiHost = $location.host()
                    } else {
                        apiHost = apiDevice.Address
                    }
                    apiPort = apiDevice.Port
                    apiKey = apiDevice.Mode2

                    return;
                });
        }

        function checkDeCONZsetup() {
            return onInit.then(function() {
                var deferred = $q.defer();
                console.log('Checking DeCONZdsetup')

                url = 'https://phoscon.de/discover'

                $http({
                    method: 'GET',
                    url: url,

                }).then(function successCallback(response) {
                    // console.log('deCONZ: Discover Recieved')
                    // console.log('response Data:' + angular.toJson(response.data, true))

                    deferred.resolve(response.data)
                    },function errorCallback(response) {
                    console.error('Error getting deCONZ Discover data:' + angular.toJson(response, true) )
                    bootbox.alert('<h2>' + $.t('Error getting deCONZ Discover data') + '</h2><br>' +
                    '<a target="_blank" href="https://phoscon.de/discover">https://phoscon.de/discover</a>')
                    deferred.reject(response)
                });

            return deferred.promise;
        });
        }

        function getDeCONZdata(deviceClass, id = '') {
            var url;

            return onInit.then(function() {
                var deferred = $q.defer();
                // console.log('getDeCONZdata')

                if (apiKey !== "") {
                    url = 'http://' + apiHost + ':' + apiPort + '/api/' + apiKey + '/' + deviceClass + '/' + id
                    // console.log('GET API URL is: ' + url)
                    $http({
                        method: 'GET',
                        url: url,

                    }).then(function successCallback(response) {
                        // console.log('deCONZ: Data Recieved')
                        // As there is no IDX and the API requires an ID, we must add back the ID to the array
                        keys = Object.keys(response.data)

                        if (deviceClass == "alarmsystems") {
                            //hack
                            // response.data['1'].devices = {"ec:1b:bd:ff:fe:6f:c3:4d-01-0501": {"armmask": "none"}};
                            // Make header
                            response.data['1'].id = keys[i]
                            response.data['1'].uniqueid = 'Master'
                            response.data['1'].name = 'Alarm System ' + 'Master'
                            response.data['1'].deviceclass = deviceClass
                            response.data['1'].type = 'Alarm System Control'
                            // Make fields, disabled
                            if (false) {
                                keys = Object.keys(response.data['1']['devices'])
                                for (i = 0; i < keys.length; i++) {
                                    response.data[keys[i]].id = keys[i]
                                    response.data[keys[i]].uniqueid = keys[i]
                                    response.data[keys[i]].name = 'Alarm System ' + keys[i]
                                    response.data[keys[i]].deviceclass = keys[i].armmask
                                    response.data[keys[i]].type = 'Alarm System'
                                }
                            }
                        }
                        else if (deviceClass != "config") {
                            // loop through count
                            for (i = 0; i < keys.length; i++) {
                                // add id to each object
                                response.data[keys[i]].id = keys[i]
                                // add class type to allow puts
                                response.data[keys[i]].deviceclass = deviceClass
                            }
                        }

                        deferred.resolve(response.data)
                        },function errorCallback(response) {
                        // console.log('Error getting deCONZ data:' + response )
                        deferred.reject(response)
                    });
                }

            return deferred.promise;
        });
        }

        function setDeCONZdata(deviceClass, method, id = '', body = '', url2 ='') {
            var url;
            if (url2) {
                url2 = '/' + url2 ;
            }

            return onInit.then(function() {
                var deferred = $q.defer();
                // console.log('setDeCONZdata')

                if (apiKey !== "") {
                    url = 'http://' + apiHost + ':' + apiPort + '/api/' + apiKey + '/' + deviceClass + '/' + id + url2
                    // console.log('SET API URL is: ' + url)
                    $http({
                        method: method,
                        url: url,
                        data: body,

                    }).then(function successCallback(response) {
                        // console.log('deCONZ: Data Recieved')
                        // console.log('response Data:' + angular.toJson(response.data, true))

                        deferred.resolve(response.data)
                        },function errorCallback(response) {
                        // console.log('Error getting deCONZ data:' + response )
                        deferred.reject(response)
                    });
                }

            return deferred.promise;
        });
        }

        function postDeCONZdata(host, port, endpoint, body, gwPass) {

            return onInit.then(function() {
                var deferred = $q.defer();

                token = btoa('delight:' + gwPass)

                if (apiHost !== "") {

                    url = 'http://' + host + ':' + port + '/' + endpoint
                    // console.log('POST API URL is: ' + 'http://' + host + ':' + port + '/' + endpoint)
                    $http({
                        method: 'POST',
                        url: url,
                        headers: {
                            'Authorization': 'Basic ' + token
                        },
                        data: body,

                    }).then(function successCallback(response) {
                        // console.log('deCONZ: Data Recieved')
                        // console.log('response Data:' + angular.toJson(response.data, true))
                        deferred.resolve(response.data)
                        },function errorCallback(response) {
                        console.error('Error getting deCONZ data:' + angular.toJson(response.data, true) )
                        bootbox.alert('<h2>' + $.t('Error getting API key') + '</h2><br>' +
                        '<p>' + $.t('This could also indicate a bad password.') + '</p>' +
                        '<pre>' + angular.toJson(response.data, true) + '</pre>')
                        deferred.reject(response)
                    });
                }

            return deferred.promise;
        });
        }

        function sendRequest(command, params) {
            return onInit.then(function() {
                var deferred = $q.defer();
                var requestId = ++requestsCount;

                var requestInfo = {
                    requestId: requestId,
                    deferred: deferred,
                };

                requestsQueue.push(requestInfo);

                return deferred.promise;
            });
        }

        function handleResponse(data) {
            if (data.type !== 'response' && data.type !== 'status') {
                return;
            }

            var requestIndex = requestsQueue.findIndex(function(item) {
                return item.requestId === data.requestId;
            });

            if (requestIndex === -1) {
                return;
            }

            var requestInfo = requestsQueue[requestIndex];

            if (data.type === 'status') {
                requestInfo.deferred.notify(data.payload);
                return;
            }

            if (data.isError) {
                requestInfo.deferred.reject(data.payload);
            } else {
                requestInfo.deferred.resolve(data.payload);
            }

            requestsQueue.splice(requestIndex, 1);
        }
    })

    function zzDeconzPluginsTableController($scope, $uibModal, $element, bootbox, dataTableDefaultSettings) {
        var $ctrl = this;
        var table;

        $ctrl.$onInit = function() {
            table = $element.find('table').dataTable(Object.assign({}, dataTableDefaultSettings, {
                autoWidth: false,
                order: [[2, 'asc']],
                paging: true,
                columns: [
                    { title: 'ID', data: 'uniqueid', "defaultContent": "" },
                    { title: 'Name', data: 'name'},
                    { title: 'Manufacturer', data: 'manufacturername', "defaultContent": "" },
                    { title: 'Model', data: 'modelid', "defaultContent": "" },
                    { title: 'Type', data: 'type'},
                    { title: 'Firmware', data: 'swversion', "defaultContent": "" },
                    { title: 'Last Seen', data: 'lastseen', "defaultContent": "" },

                    {
                        title: '',
                        className: 'actions-column',
                        width: '80px',
                        data: '',
                        orderable: false,
                        render: actionsRenderer
                    },
                ],
            }));

            table.on('click', '.js-rename-device', function() {
                var row = table.api().row($(this).closest('tr')).data();
                var scope = $scope.$new(true);
                scope.device = row;

                $uibModal
                    .open(Object.assign({ scope: scope }, renameDeviceModal)).result.then(closedCallback, dismissedCallback);

                    function closedCallback(){
                      // Do something when the modal is closed
                    //   console.log('closed callback')
                    }

                    function dismissedCallback(){
                      // Do something when the modal is dismissed
                    //   console.log('cancelled callback')
                    }

                $scope.$apply();

            });

            table.on('click', '.js-include-device', function() {
                var row = table.api().row($(this).closest('tr')).data();
                var scope = $scope.$new(true);
                scope.device = row;

                $uibModal
                    .open(Object.assign({ scope: scope }, includeDeviceModal)).result.then(closedCallback, dismissedCallback);

                    function closedCallback(){
                      // Do something when the modal is closed
                    //   console.log('closed callback')
                    }

                    function dismissedCallback(){
                      // Do something when the modal is dismissed
                    //   console.log('cancelled callback')
                    }

                $scope.$apply();

            });

            table.on('click', '.js-includerem-device', function() {
                var row = table.api().row($(this).closest('tr')).data();
                var scope = $scope.$new(true);
                scope.device = row;

                $uibModal
                    .open(Object.assign({ scope: scope }, includeremDeviceModal)).result.then(closedCallback, dismissedCallback);

                    function closedCallback(){
                      // Do something when the modal is closed
                    //   console.log('closed callback')
                    }

                    function dismissedCallback(){
                      // Do something when the modal is dismissed
                    //   console.log('cancelled callback')
                    }

                $scope.$apply();

            });

            table.on('click', '.js-config-device', function() {
                var row = table.api().row($(this).closest('tr')).data();
                var scope = $scope.$new(true);
                scope.device = row;

                $uibModal
                    .open(Object.assign({ scope: scope }, configDeviceModal)).result.then(closedCallback, dismissedCallback);

                    function closedCallback(){
                      // Do something when the modal is closed
                    //   console.log('closed callback')
                    }

                    function dismissedCallback(){
                      // Do something when the modal is dismissed
                    //   console.log('cancelled callback')
                    }

                $scope.$apply();

            });

            table.on('click', '.js-device-data', function() {
                var device = table.api().row($(this).closest('tr')).data();

                bootbox.alert('<pre>' + angular.toJson(device, true) + '</pre>')
            });

            table.on('click', '.js-remove-device', function() {
                var row = table.api().row($(this).closest('tr')).data();
                var scope = $scope.$new(true);
                scope.device = row;

                $uibModal
                    .open(Object.assign({ scope: scope }, deleteDeviceModal))

                $scope.$apply();
            });

            render($ctrl.zigdevs);
        }

        $ctrl.$onChanges = function(changes) {
            if (changes.zigdevs) {
                render($ctrl.zigdevs);
            }
        };

        function render(items) {
            if (!table || !items) {
                return;
            }

            table.api().clear();
            table.api().rows
                .add(items)
                .draw();
        }

        function actionsRenderer(value, type, device) {
            var actions = [];
            var delimiter = '<img src="../../images/empty16.png" width="16" height="16" />';
            if (device.deviceclass == 'alarmsystems') {
                actions.push('<button class="btn btn-icon js-include-device" title="' + $.t('Add Device') + '"><img src="images/add.png" /></button>');
            }
            else {
                actions.push('<button class="btn btn-icon js-rename-device" title="' + $.t('Rename Device') + '"><img src="images/rename.png" /></button>');
            }
            if (device.deviceclass == 'sensors' || device.deviceclass == 'alarmsystems') {
                actions.push('<button class="btn btn-icon js-config-device" title="' + $.t('Configure Device') + '"><img src="images/devices.png" /></button>');
            }
            actions.push('<button class="btn btn-icon js-device-data" title="' + $.t('Device Data') + '"><img src="images/log.png" /></button>');
            if (device.deviceclass == 'alarmsystems') {
                actions.push('<button class="btn btn-icon js-includerem-device" title="' + $.t('Remove Device') + '"><img src="images/delete.png" /></button>');
            }
            else {
                actions.push('<button class="btn btn-icon js-remove-device" title="' + $.t('Remove') + '"><img src="images/delete.png" /></button>');
            }

            return actions.join('&nbsp;');
        }
    }
});
