/* global angular */
var ng_messages = angular.module('ng_messages', ['ngTable']);

ng_messages.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

ng_messages.controller('ListCtrl', function ListCtrl($scope, $log, $http){
    // just dummy init function
    $scope.initialize = function(data){
        $log.log('initialize', data);
        $scope.initData = data;
    };

    $scope.loadItems = function(){
        $http.get('/api/v1/messages/')
            .then(function(response){
                $scope.items = response.data;
            });
        $log.log('loadItems', $scope.items);
    };

    $scope.loadItems();

    $scope.saveItem = function(){

    };
});