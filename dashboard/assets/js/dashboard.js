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
    transactionCell.innerHTML = e.description + (e.party_name?' (' + e.party_name + ') ':'') + '<div class="text-right">category: ' + e.category__name + '</div>' +
            '<div class="text-right">account: ' + e.account__bank__name + ' - ' + e.account__name + '; type: ' + e.type + '</div>';
    rowToFill.appendChild(transactionCell);

    // amount
    amountCell = document.createElement("td");
    amountCell.setAttribute('class','text-right');
    if (!e.approved) {
        amountCell.setAttribute('class','text-right not-approved');
    }
    amountCell.innerHTML = e.amount_account_currency + ' ' + e.account__currency__name;
    if (e.account__currency__name != 'PLN') {
        amountCell.innerHTML += '<br />' + e.amount + ' PLN';
    }
    if (!e.approved) {
        amountCell.innerHTML += '<button onclick="change_approval(' + e.id + '); return false;" class="btn btn-warning btn-sm">&#10004;</button>';
    }
    rowToFill.appendChild(amountCell);

    return rowToFill;
}

function fill_transactions(data) {
    var bodyToFill = $('#transactions_table tbody');
    var lastDate;
    var t = data.transactions_list;
    var divideDates = (document.filters.sort_order.value == 'date' || document.filters.sort_order.value == '-date');

    document.filters.start_date.value = data.start_date;
    document.filters.end_date.value = data.end_date;

    bodyToFill.empty();
    transactions = [];

    t.forEach(function(e){
        transactions[e.id] = e;
        thisRow = document.createElement("tr");
        thisRow.setAttribute('data-transaction-id', e.id);
        if (lastDate != e.date) {
            if (divideDates) {
                thisRow.style.borderTop = "4px solid black";
            }
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
    document.filters.start_date.value = "";
    document.filters.end_date.value = "";
    load_transactions();
    load_months();
    load_accounts_balance();
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
                load_accounts_balance();
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

    // fill form
    $('#tr_account').empty();
    $('#ft_account option').clone().appendTo('#tr_account');
    $('#tr_account option')[0].remove();

    if (transactions[t_id]) {
        $('#tr_account').val(transactions[t_id].account__id);
        $('#tr_date').val(transactions[t_id].date);
        $('#tr_amount').val(transactions[t_id].amount_account_currency);
        $('#tr_description').val(transactions[t_id].description);
        $('#tr_irrelevant').prop('checked', transactions[t_id].irrelevant);

        if (transactions[t_id].irrelevant) {
            $('#transactionsModal .relevancy').html("Set as relevant");
        } else {
            $('#transactionsModal .relevancy').html("Set as irrelevant");
        }

        $('#transactionsModal .relevancy').show();
        $('#transactionsModal .tr-save').show();
    } else {
        $('#transactionsModal .relevancy').hide();
        $('#transactionsModal .tr-save').hide();
    }
}

function tr_save(is_new) {
    // ajax save transaction, update table
    document.transaction_edit.tr_id.value = (is_new ? 0 : $('#transactionsModal').data('transaciton-id'));
    data_to_send = $(document.transaction_edit).serialize();

    $.ajax({
        type: 'POST',
        url: '/transactions/save/',
        data: data_to_send,
        success: function(data) {
            $('#transactionsModal').modal('toggle');

            if (data.t != $('#transactionsModal').data('transaciton-id')) {
                // reload all
            } else {
                // update this transaction only
            }

            load_transactions();
            load_months();
            load_accounts_balance();
        },
        dataType: 'json',
        failure: function(errMsg) {
            alert(errMsg);
        }
    });
}

function set_click_on_months() {
    $('.monthlyReview li span').on('click',function(e){
        // calculate
        dateArr = $(this).data('date').split('-');
        firstDay = new Date(dateArr[0], dateArr[1]-1, 1);
        lastDay = new Date(dateArr[0], dateArr[1], 0);
        // fill
        document.filters.start_date.value = firstDay.yyyymmdd();
        document.filters.end_date.value = lastDay.yyyymmdd();
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

function change_approval(t_id) {
    if (transactions[t_id]) {
        $.ajax({
            type: 'POST',
            url: '/transactions/change_approval/',
            data: { 't_id' : t_id,
                    'a_to_set' : ! transactions[t_id].approved },
            success: function(data) {
                transactions[t_id].approved = data.a_set;
                thisRow = $('tr[data-transaction-id=' + t_id + ']');
                thisRow.empty();
                thisRow = fill_transaction_row(transactions[t_id], thisRow[0]);
            },
            dataType: 'json',
            failure: function(errMsg) {
                alert(errMsg);
            }
        });
    }
}

function load_accounts_balance() {
    fetch('/account_balance/')
        .then(response => response.text())
        .then(html => {
            document.getElementById('accountAccordion').innerHTML = html;
        });
}

var transactions = [];

$(function(){
    load_transactions();
    load_months();
    load_accounts_balance();

    $('#transactions_table .date-header').on("click",function(){
        $('#transactions_table th').removeClass('activeUp').removeClass('activeDown');
        if (document.filters.sort_order.value == '-date') {
            document.filters.sort_order.value = 'date';
            $('#transactions_table .date-header').addClass('activeDown');
        } else {
            document.filters.sort_order.value = '-date';
            $('#transactions_table .date-header').addClass('activeUp');
        }
        load_transactions();
    });

    $('#transactions_table .amount-header').on("click",function(){
        $('#transactions_table th').removeClass('activeUp').removeClass('activeDown');
        if (document.filters.sort_order.value == 'amount') {
            document.filters.sort_order.value = '-amount';
            $('#transactions_table .amount-header').addClass('activeUp');
        } else {
            document.filters.sort_order.value = 'amount';
            $('#transactions_table .amount-header').addClass('activeDown');
        }
        load_transactions();
    });
});