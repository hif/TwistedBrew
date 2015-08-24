'use strict';

twistedBrew.controller('MessageController', function MessageController($scope, $log, $http, $routeParams){

    $scope.type = $routeParams.type;
    if(!$scope.type)
        $scope.type = "";

    $scope.loadItems = function(){
        $http({
            url: '/api/v1/messages/',
            method: "GET",
            params: {type: $scope.type}
        })
        //$http.get('/api/v1/messages/')
        .then(function(response){
            $scope.items = response.data;
        });
        $log.log('loadItems', $scope.items);
    };

    $scope.loadItems();

    $scope.saveItem = function(){

    };
});