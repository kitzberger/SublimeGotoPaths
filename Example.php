<?php

view(
    'backpack::crud.partials.stock-details-row',
    [
        'entry' => $entry,
        'crud' => $this->crud
    ]
)->render();
