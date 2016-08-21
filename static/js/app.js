var app = angular.module('cyberfront', ['ngRoute']);

// Custom Services

app.service('api', function($http) {
    var self = this;

    this.services = {};
    this.vulns = {};
    this.hosts = {};
    this.worlds = {};
    this.oses = {};

    this.updateOperatingSystems = function() {
        return $http.get('/api/os').success(function(data) {
            data.forEach(function(os) {
                self.oses[os._id.$oid] = os;
            })
        })
    };

    this.updateVulns = function() {
        return $http.get('/api/vulns').success(function(data) {
            data.forEach(function(vuln) {
                self.vulns[vuln._id.$oid] = vuln;
            });
        })
    };

    this.updateServices = function() {
        return $http.get('/api/services').success(function(data) {
            data.forEach(function(service) {
                self.services[service._id.$oid] = service;
            });
        })
    };

    this.updateWorlds = function() {
        return new Promise(function(resolve, reject) {
            $http.get('/api/worlds').success(function (data) {
                var requests = [];

                data.forEach(function (world) {
                    var world_id = world._id.$oid;
                    self.worlds[world_id] = world;

                    requests.push($http.get('/api/worlds/' + world_id + '/hosts').success(function (host_data) {
                        var hs = {};
                        host_data.hosts.forEach(function (host) {
                            self.hosts[host._id.$oid] = host;
                            hs[host._id.$oid] = host;
                        });
                        self.worlds[world_id].hosts = hs;
                    }));

                    console.log(self.worlds);
                });

                Promise.all(requests).then(function() {
                    resolve()
                });
            });
        })
    };

    this.updateHost = function(host) {
        self.hosts[host._id.$oid] = host;
        self.worlds[host.world._id.$oid].hosts[host._id.$oid] = host;
    };

    this.doUpdate = function() {
        console.log('updating api');
        var s = self.updateServices();
        var w = self.updateWorlds();
        var v = self.updateVulns();
        var o = self.updateOperatingSystems();

        return Promise.all([s, w, v, o]);
    };

    this.getService = function(service_id) {
        return new Promise(function(resolve, reject) {
            if (self.promise) {
                self.promise.then(function() {
                    resolve(self.services[service_id]);
                })
            } else {
                resolve(self.services[service_id]);
            }
        });
    };

    this.getServices = function () {
        return new Promise(function(resolve, reject) {
            if (self.promise) {
                self.promise.then(function() {
                    resolve(self.services);
                })
            } else {
                resolve(self.services);
            }
        });
    };

    this.getWorld = function (world_id) {
        return new Promise(function(resolve, reject) {
            if (self.promise) {
                self.promise.then(function(_) {
                    console.log('resolving');
                    console.log(self.worlds[world_id]);
                    resolve(self.worlds[world_id]);
                })
            } else {
                console.log(self.worlds);
                console.log(self.worlds[world_id]);
                console.log(world_id);
                resolve(self.worlds[world_id]);
            }
        });
    };

    this.getWorlds = function() {
        return new Promise(function(resolve, reject) {
            if (self.promise) {
                self.promise.then(function(_) {
                    resolve(self.worlds);
                })
            } else {
                resolve(self.worlds);
            }
        });
    };

    this.getHost = function(id) {
        return new Promise(function(resolve, reject) {
            if (self.promise) {
                self.promise.then(function() {
                    console.log(self.hosts);
                    console.log('asdf');
                    resolve(self.hosts[id]);
                })
            } else {
                resolve(self.hosts[id]);
            }
        });
    };

    this.update = function() {
        self.promise = this.doUpdate();
        self.promise.then(function(data) {
            self.promise = null;
        });
    };

    this.update();
});

// Custom Directives

app.directive('navbar', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/templates/navbar.html',
        controller: function($scope, api) {
            api.getWorlds().then(function(worlds) {
                $scope.$apply(function() {
                    console.log('navbar promise returned');
                    console.log(worlds);
                    $scope.worlds = worlds;
                });
            })
        }
    }
});

app.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        scope: {
            files: "="
        },
        link: function(scope, element, attrs) {
            var key = attrs.fileModel;

            element.bind('change', function() {
                scope.$apply(function() {
                    scope.files[key] = element[0].files[0];
                });
            });
        }
    };
}]);

app.directive('cfServiceRow', function() {
    return {
        restrict: 'A',
        templateUrl: '/static/templates/directives/cf-service-row.html',
        scope: {
            service: '='
        },
        controller: function($scope, api) {
            $scope.source = api.services[$scope.service.source.$oid];

            $scope.pretty = {
                name: $scope.source.service_name,
                version: $scope.source.version
            }
        }
    }
});

app.directive('cfHeader', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/templates/header.html',
        scope: {
            title: '@',
            subtitle: '@'
        }
    }
});

app.directive('switchWrapper', function() {
    return {
        restrict: 'A',
        scope: {
            model: '='
        },
        link: function(scope, elem, attrs) {
            elem.bootstrapSwitch();
            scope.model = attrs.checked;

            elem.on('switchChange.bootstrapSwitch', function(event, state) {
                scope.$apply(function() {
                    scope.model = state;
                });
            });
        }
    }
});

app.directive('cfModalAccount', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/templates/modal/account.html',
        scope: {
            host: '=',
            user: '='
        },
        controller: function($scope, $http) {
            $scope.post_account = function() {
                var params = {
                    action: 'ACCOUNT',
                    account: $scope.user
                };

                var fd = new FormData();
                fd.append('json', angular.toJson(params));

                $http.post('/api/hosts/' + $scope.host._id.$oid, fd,
                    {
                        transformRequest: angular.identity,
                        headers: {
                            'Content-Type': undefined
                        }
                    }).success(function(data) {
                    $scope.host = data;
                });
            };
        }
    }
});

app.directive('cfModalModuleInstaller', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/templates/modal/service.html',
        scope: {
            host: '=',
            selected: '=',
            out: '=options',
            choices: '=',
            type: '='
        },
        controller: function($scope, $http, api) {
            $scope.files = {};
            $scope.services = api.services;

            $scope.choicedebug = function() {
                console.log($scope.choices);
            };

            $scope.select = function(service) {
                $scope.selected = service;

                $scope.host.services.forEach(function(s) {
                    if (service.name == s.name) {
                        $scope.out = s.options;
                    }
                });

                $scope.host.vulnerabilities.forEach(function(v) {
                    if (service.name == v.name) {
                        $scope.out = v.options;
                    }
                })
            };

            $scope.post_service = function() {
                var fd = new FormData();

                var params = {
                    module: $scope.selected._id.$oid,
                    options: $scope.out,
                    action: 'MODULE'
                };

                fd.append('json', angular.toJson(params));

                Object.keys($scope.files).forEach(function(key) {
                    fd.set(key, $scope.files[key]);
                });

                $http.post('/api/hosts/' + $scope.host._id.$oid, fd, {
                    transformRequest: angular.identity,
                    headers: {
                        'Content-Type': undefined
                    }
                }).success(function(data) {
                    $scope.host = data;
                    api.updateHost(data);
                }).error(function(data) {
                    console.log(data);
                })
            }
        }
    }
});

app.directive('objectTable', function() {
    return {
        restrict: 'E',
        template: '<p ng-repeat="option in l">{{option.key}}: {{option.value}}</p>',
        scope: {
            obj: '='
        },
        controller: function($scope) {
            var l = [];

            Object.keys($scope.obj).forEach(function(key) {
                l.push({'key': key, 'value': $scope.obj[key]})
            });

            $scope.l = l;
        }
    }
});


// Url Routing

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider

        // Index page
        .when('/', {
            templateUrl: '/static/templates/index.html',
            controller: function(api) {
                // I'm just here so I won't get fined.
            }
        })

        // View world page
        .when('/view-world/:world_id', {
            templateUrl: '/static/templates/view-world.html',
            controller: function($scope, $routeParams, api) {
                var world_id = $routeParams.world_id;

                $scope.clicked = function(host, action) {
                    console.log(host.hostname);
                };

                api.getWorld(world_id).then(function(world) {
                    $scope.$apply(function() {
                       $scope.world = world;
                    });
                });
            }
        })

        // View Host
        .when('/view-host/:world_id/:host_id', {
            templateUrl: '/static/templates/view-host.html',
            controller: function($scope, $routeParams, api) {
                var host_id = $routeParams.host_id;
                var world_id = $routeParams.world_id;

                $scope.user = {};
                $scope.selected = {full_name: 'Select a Service'};
                $scope.options = {};
                $scope.choices = [];
                $scope.services = api.services;
                $scope.vulns = api.vulns;

                api.getHost(host_id).then(function(host) {
                    $scope.$apply(function() {
                        $scope.host = host;
                    })
                });

                api.getWorld(world_id).then(function(world) {
                    $scope.$apply(function() {
                        $scope.world = world;
                    });
                });

                $scope.editUser = function(u) {
                    $scope.user = u;
                };

                $scope.editService = function(s) {
                    $scope.selected = $scope.services[s.source._ref.$id.$oid];
                    $scope.options = s.options;
                    $scope.choices = $scope.services;
                }
            }
        })

        // Add host page
        .when('/add-host/:world_id', {
            templateUrl: '/static/templates/add-host.html',
            controller: function($scope, $http, $routeParams, api) {
                $scope.selected_os = {name: 'Operating System', version: ''};
                $scope.hostname = '';
                $scope.oses = api.oses;

                api.getWorld($routeParams.world_id).then(function(world) {
                    $scope.world = world;
                });

                $scope.select = function(os) {
                    $scope.selected_os = os;
                };

                $scope.submit = function() {
                    var params = {hostname: $scope.hostname, os: $scope.selected_os._id.$oid};

                    $http.post('/api/worlds/' + $scope.world._id.$oid + '/hosts', params).success(function(data) {
                        console.log(data);
                    });
                };
            }
        });

        //.when('/')
}]);
