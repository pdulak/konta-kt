Date.prototype.yyyymmdd = function() {
    var yyyy = this.getFullYear();
    var mm = this.getMonth() < 9 ? "0" + (this.getMonth() + 1) : (this.getMonth() + 1); // getMonth() is zero-based
    var dd  = this.getDate() < 10 ? "0" + this.getDate() : this.getDate();
    return "".concat(yyyy).concat("-").concat(mm).concat("-").concat(dd);
};

function fill_transaction_row(e, rowToFill) {
    // date
    dateCell = document.createElement("td");
    $(dateCell).html(e.date + '<div class="buttons"><button onclick="transaction_menu(' + e.id + '); return false;" class="btn btn-light btn-sm">&#9874;</button>'
        + '<button onclick="change_relevancy(' + e.id + '); return false;" class="btn btn-warning btn-sm">R</button></div>');
    rowToFill.appendChild(dateCell);

    // transaction
    transactionCell = document.createElement("td");
    transactionCell.setAttribute('data-irrelevant','0');
    if (e.irrelevant) {
        transactionCell.style.color = '#aaa';
        transactionCell.setAttribute('data-irrelevant','1');
    }
    transactionCell.innerHTML = e.description + '<div class="text-right">category: ' + e.category__name + '</div>' +
            '<div class="text-right">account: ' + e.account__bank__name + ' - ' + e.account__name + '; type: ' + e.type + '</div>';
    rowToFill.appendChild(transactionCell);

    // amount
    amountCell = document.createElement("td");
    amountCell.setAttribute('class','text-right');
    amountCell.innerHTML = e.amount_account_currency + ' ' + e.account__currency__name;
    rowToFill.appendChild(amountCell);

    return rowToFill;
}

function fill_transactions(data) {
    var bodyToFill = $('#transactions_table tbody');
    var lastDate;
    var t = data.transactions_list;

    document.filters.startDate.value = data.startDate;
    document.filters.endDate.value = data.endDate;

    bodyToFill.empty();
    transactions = [];

    t.forEach(function(e){
        transactions[e.id] = e;
        thisRow = document.createElement("tr");
        thisRow.setAttribute('data-transaction-id', e.id);
        if (lastDate != e.date) {
            thisRow.style.borderTop = "4px solid black";
            lastDate = e.date;
        }

        thisRow = fill_transaction_row(e, thisRow);

        bodyToFill.append(thisRow);
    });
}

function load_transactions() {
    $('#transactions_table').addClass('loading');

    $.ajax({
        type: 'POST',
        url: '/j_transactions/',
        data: $(document.filters).serialize(),
        success: function(data) {
            if (data.transactions_list) {
                fill_transactions(data);
            } else {
                alert('transactions not loaded');
            }
            $('#transactions_table').removeClass('loading');
        },
        dataType: 'json',
        failure: function(errMsg) {
            $('#transactions_table').removeClass('loading');
            alert(errMsg);
        }
    });
}

function reset_filters() {
    document.filters.irrelevant.selectedIndex = 0;
    document.filters.direction.selectedIndex = 0;
    if (document.filters.account.tagName == "SELECT") {
        document.filters.account.selectedIndex = 0;
    }
    document.filters.startDate.value = "";
    document.filters.endDate.value = "";
    load_transactions();
}

function change_relevancy_modal() {
    change_relevancy($('#transactionsModal').data('transaciton-id'));
    $('#transactionsModal').modal('toggle');
}

function change_relevancy(t_id) {
    if (transactions[t_id]) {
        $.ajax({
            type: 'POST',
            url: '/transactions/change_relevancy/',
            data: { 't_id' : t_id,
                    'r_to_set' : ! transactions[t_id].irrelevant },
            success: function(data) {
                transactions[t_id].irrelevant = data.r_set;
                thisRow = $('tr[data-transaction-id=' + t_id + ']');
                thisRow.empty();
                thisRow = fill_transaction_row(transactions[t_id], thisRow[0]);
                load_months();
            },
            dataType: 'json',
            failure: function(errMsg) {
                alert(errMsg);
            }
        });
    }
}

function transaction_menu(t_id) {
    $('#transactionsModal').modal();
    $('#transactionsModal').data('transaciton-id',t_id);

    if (transactions[t_id].irrelevant) {
        $('#transactionsModal .relevancy').html("Set as relevant");
    } else {
        $('#transactionsModal .relevancy').html("Set as irrelevant");
    }
}

function set_click_on_months() {
    $('.monthlyReview li span').on('click',function(e){
        // calculate
        dateArr = $(this).data('date').split('-');
        firstDay = new Date(dateArr[0], dateArr[1]-1, 1);
        lastDay = new Date(dateArr[0], dateArr[1], 0);
        // fill
        document.filters.startDate.value = firstDay.yyyymmdd();
        document.filters.endDate.value = lastDay.yyyymmdd();
        // execute reload
        load_transactions();
    });
}

function load_months() {
    $.ajax({
        type: 'POST',
        url: '/transactions/months/',
        success: function(data) {
            var m = data.months;
            $('.monthlyReview').empty();
            bodyToFill = $('.monthlyReview')[0];

            m.forEach(function(e){
                thisRow = document.createElement("div");
                thisRow.innerHTML = '<span class="month" data-date="' + e.month.substring(0,7) + '">' + e.month.substring(0,7) + '</span>'
                    + ' <span class="total">' + Math.round(e.total * 100)/100 + '</span>'
                    + ' <span class="up">&#9651; ' + Math.round(e.up * 100)/100 + '</span>'
                    + ' <span class="down">&#9661; ' + Math.round(e.down * 100)/100 + '</span>';

                bodyToFill.append(thisRow);
            });

            set_click_on_months();
        }
    })


}

var transactions = [];

$(function(){
    load_transactions();
    load_months();
});