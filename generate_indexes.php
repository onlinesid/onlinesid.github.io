<?php 

$words = json_decode(file_get_contents('./words_dictionary.json'), true);

$by_length = [];
foreach ($words as $w => $i) {
    $len = strlen($w);
    //if ($len >= 4 && $len < 16) {
        $by_length['length_'.$len][] = $w;
    //}
    echo '.';
}
echo "\n";

file_put_contents("./words_dictionary_indexed.json", json_encode($by_length, JSON_PRETTY_PRINT));

foreach ($by_length as $len => $words) {
    echo "$len : ".count($words)." words\n";
}


