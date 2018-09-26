import { Component, EventEmitter, OnInit, OnDestroy, Output } from '@angular/core';

import { Subscription } from "rxjs/internal/Subscription";
import { faArrowLeft, faSearch } from '@fortawesome/free-solid-svg-icons';

import { SkillsService } from "../skills.service";

@Component({
    selector: 'market-skill-toolbar',
    templateUrl: './skill-toolbar.component.html',
    styleUrls: ['./skill-toolbar.component.scss']
})
export class SkillToolbarComponent implements OnInit, OnDestroy {
    public backArrow = faArrowLeft;
    public languages = [
        {value: 'english', display: 'English'}
    ];
    public searchIcon = faSearch;
    @Output() public searchResults = new EventEmitter();
    public searchTerm: string;
    public selectedLanguage = this.languages[0].value;
    public skillsAreFiltered: Subscription;
    public showBackButton: boolean = false;

    constructor(private skillsService: SkillsService) { }

    ngOnInit() {
        this.skillsAreFiltered = this.skillsService.isFiltered.subscribe(
            (isFiltered) => { this.onFilteredStateChange(isFiltered) }
        );
    }

    ngOnDestroy() {
        this.skillsAreFiltered.unsubscribe();
    }

    clearSearch(): void {
        this.searchTerm = '';
        this.searchSkills()
    }

    searchSkills(): void {
        this.skillsService.searchSkills(this.searchTerm).subscribe(
            (skills) => {
                this.searchResults.emit(skills);
                console.log(this.skillsAreFiltered);
            }
        );
    }

    onFilteredStateChange (isFiltered) {
        this.showBackButton = isFiltered
    }
}
