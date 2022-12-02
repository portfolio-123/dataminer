def custom_paste(event, data):
    try:
        event.widget.delete('sel.first', 'sel.last')
    except Exception:
        pass
    event.widget.insert('insert', data if data is not None else event.widget.clipboard_get())
    return 'break'
